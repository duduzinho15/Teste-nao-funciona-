#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURADOR AUTOMÁTICO DO POSTGRESQL
====================================

Script para configurar automaticamente o PostgreSQL no Windows, incluindo:
- Inicialização do serviço PostgreSQL
- Configuração do PATH do sistema
- Criação de banco de dados e usuário
- Configuração de variáveis de ambiente

Autor: Assistente de Configuração
Data: 2025-08-07
Versão: 2.0
"""

import os
import sys
import subprocess
import ctypes
import winreg
import shutil
import time
from pathlib import Path

# Configuração de logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('configuracao_postgres.log')
    ]
)
logger = logging.getLogger(__name__)

class ConfiguradorPostgreSQL:
    def __init__(self):
        self.postgres_versions = ['17', '16', '15', '14', '13', '12']
        self.postgres_paths = [
            r"C:\Program Files\PostgreSQL\{}\bin",
            r"C:\Program Files (x86)\PostgreSQL\{}\bin"
        ]
        self.postgres_service = "postgresql-x64-{}"
        self.postgres_install_path = None
        self.postgres_version = None
        self.is_admin = self.check_admin()
        
        # Configurações do banco de dados
        self.db_name = "apostapro_db"
        self.db_user = "apostapro_user"
        self.db_password = "apostapro_pass123"
        self.db_host = "localhost"
        self.db_port = "5432"
    
    def check_admin(self):
        """Verifica se o script está sendo executado como administrador"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def run_command(self, command, shell=True, capture_output=True):
        """Executa um comando e retorna o resultado"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=capture_output,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            return None
    
    def find_postgres(self):
        """Localiza a instalação do PostgreSQL no sistema"""
        logger.info("Procurando instalação do PostgreSQL...")
        
        # Verifica versões do PostgreSQL
        for version in self.postgres_versions:
            for path_template in self.postgres_paths:
                path = path_template.format(version)
                if os.path.exists(path):
                    psql_path = os.path.join(path, 'psql.exe')
                    if os.path.exists(psql_path):
                        self.postgres_install_path = path
                        self.postgres_version = version
                        logger.info(f"PostgreSQL {version} encontrado em: {path}")
                        return True
        
        logger.error("PostgreSQL não encontrado no sistema.")
        return False
    
    def add_to_path(self):
        """Adiciona o diretório bin do PostgreSQL ao PATH do sistema"""
        if not self.postgres_install_path:
            logger.error("Caminho do PostgreSQL não definido.")
            return False
            
        try:
            # Obtém o PATH atual do sistema
            with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
                with winreg.OpenKey(
                    hkey, 
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                    0, 
                    winreg.KEY_READ | winreg.KEY_WRITE
                ) as key:
                    path_value, _ = winreg.QueryValueEx(key, "Path")
                    
                    # Verifica se o caminho já está no PATH
                    if self.postgres_install_path.lower() not in path_value.lower():
                        new_path = f"{path_value};{self.postgres_install_path}"
                        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                        logger.info(f"Adicionado ao PATH do sistema: {self.postgres_install_path}")
                        
                        # Notifica o sistema sobre a mudança no PATH
                        ctypes.windll.user32.SendMessageW(
                            0xFFFF,  # HWND_BROADCAST
                            0x1A,    # WM_SETTINGCHANGE
                            0, 
                            "Environment"
                        )
                        return True
                    else:
                        logger.info("O diretório já está no PATH do sistema.")
                        return True
        except Exception as e:
            logger.error(f"Erro ao adicionar ao PATH: {e}")
            return False
    
    def start_postgres_service(self):
        """Inicia o serviço do PostgreSQL"""
        if not self.postgres_version:
            logger.error("Versão do PostgreSQL não definida.")
            return False
            
        service_name = self.postgres_service.format(self.postgres_version)
        logger.info(f"Iniciando serviço {service_name}...")
        
        # Verifica o status do serviço
        result = self.run_command(f"sc query {service_name}")
        if not result or "RUNNING" in result.stdout:
            logger.info("O serviço já está em execução.")
            return True
            
        # Tenta iniciar o serviço
        result = self.run_command(f"net start {service_name}")
        if result and result.returncode == 0:
            logger.info("Serviço iniciado com sucesso.")
            return True
        else:
            logger.error(f"Falha ao iniciar o serviço: {result.stderr if result else 'Erro desconhecido'}")
            return False
    
    def create_database_and_user(self):
        """Cria o banco de dados e o usuário"""
        if not self.postgres_install_path:
            logger.error("Caminho do PostgreSQL não definido.")
            return False
            
        psql_path = os.path.join(self.postgres_install_path, 'psql.exe')
        if not os.path.exists(psql_path):
            logger.error("Comando psql.exe não encontrado.")
            return False
            
        # Comandos SQL para criar usuário e banco de dados
        commands = [
            f'"{psql_path}" -U postgres -c "CREATE USER {self.db_user} WITH PASSWORD \'{self.db_password}\';"',
            f'"{psql_path}" -U postgres -c "CREATE DATABASE {self.db_name} OWNER {self.db_user};"',
            f'"{psql_path}" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user};"',
        ]
        
        for cmd in commands:
            result = self.run_command(cmd, capture_output=True)
            if result and result.returncode != 0:
                if "already exists" not in result.stderr:
                    logger.error(f"Erro ao executar comando: {result.stderr}")
                    return False
                else:
                    logger.warning(result.stderr.strip())
        
        logger.info("Banco de dados e usuário criados com sucesso.")
        return True
    
    def setup_environment_variables(self):
        """Configura as variáveis de ambiente"""
        env_vars = {
            'PGHOST': self.db_host,
            'PGPORT': self.db_port,
            'PGUSER': self.db_user,
            'PGPASSWORD': self.db_password,
            'PGDATABASE': self.db_name
        }
        
        try:
            with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
                with winreg.OpenKey(
                    hkey, 
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                    0, 
                    winreg.KEY_READ | winreg.KEY_WRITE
                ) as key:
                    for var, value in env_vars.items():
                        try:
                            current_value, _ = winreg.QueryValueEx(key, var)
                            logger.info(f"Variável {var} já existe com valor: {current_value}")
                        except WindowsError:
                            winreg.SetValueEx(key, var, 0, winreg.REG_SZ, value)
                            logger.info(f"Variável {var} definida como: {value}")
            
            # Notifica o sistema sobre as mudanças nas variáveis de ambiente
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x1A, 0, "Environment")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao configurar variáveis de ambiente: {e}")
            return False
    
    def test_connection(self):
        """Testa a conexão com o banco de dados"""
        if not self.postgres_install_path:
            logger.error("Caminho do PostgreSQL não definido.")
            return False
            
        psql_path = os.path.join(self.postgres_install_path, 'psql.exe')
        if not os.path.exists(psql_path):
            logger.error("Comando psql.exe não encontrado.")
            return False
            
        logger.info("Testando conexão com o banco de dados...")
        
        # Usa variáveis de ambiente para autenticação
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_password
        
        cmd = [
            psql_path,
            '-h', self.db_host,
            '-p', self.db_port,
            '-U', self.db_user,
            '-d', self.db_name,
            '-c', 'SELECT version();'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env
            )
            
            if result.returncode == 0:
                logger.info("✅ Conexão bem-sucedida!")
                logger.info(result.stdout.strip())
                return True
            else:
                logger.error(f"❌ Falha na conexão: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {e}")
            return False
    
    def run_setup(self):
        """Executa todo o processo de configuração"""
        logger.info("=== INÍCIO DA CONFIGURAÇÃO DO POSTGRESQL ===")
        
        if not self.is_admin:
            logger.error("Este script requer privilégios de administrador. Execute como administrador.")
            logger.info("Dica: Clique com o botão direito no arquivo e selecione 'Executar como administrador'")
            return False
        
        if not self.find_postgres():
            logger.error("Por favor, instale o PostgreSQL e tente novamente.")
            return False
        
        if not self.add_to_path():
            logger.error("Falha ao configurar o PATH do sistema.")
            return False
        
        if not self.start_postgres_service():
            logger.error("Falha ao iniciar o serviço do PostgreSQL.")
            return False
        
        if not self.create_database_and_user():
            logger.error("Falha ao criar banco de dados e usuário.")
            return False
        
        if not self.setup_environment_variables():
            logger.error("Falha ao configurar variáveis de ambiente.")
            return False
        
        if not self.test_connection():
            logger.error("Falha ao testar a conexão com o banco de dados.")
            return False
        
        logger.info("\n✅ Configuração do PostgreSQL concluída com sucesso!")
        logger.info(f"Banco de dados: {self.db_name}")
        logger.info(f"Usuário: {self.db_user}")
        logger.info(f"Senha: {self.db_password}")
        logger.info(f"Host: {self.db_host}")
        logger.info(f"Porta: {self.db_port}")
        logger.info("\nReinicie o terminal para que as alterações tenham efeito.")
        return True

if __name__ == "__main__":
    configurador = ConfiguradorPostgreSQL()
    if configurador.run_setup():
        sys.exit(0)
    else:
        sys.exit(1)
