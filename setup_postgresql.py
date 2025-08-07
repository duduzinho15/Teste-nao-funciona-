#!/usr/bin/env python3
"""
CONFIGURAÇÃO AUTOMATIZADA DO POSTGRESQL
=======================================

Script para configurar PostgreSQL automaticamente para o projeto ApostaPro.
Cria banco de dados, usuário e configura permissões.

Autor: Sistema de Migração de Banco de Dados
Data: 2025-08-03
Versão: 1.0
"""

import subprocess
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostgreSQLSetup:
    """Classe para configuração automatizada do PostgreSQL."""
    
    def __init__(self):
        self.db_name = "apostapro_db"
        self.db_user = "apostapro_user"
        self.db_password = "apostapro_pass"
        self.db_host = "localhost"
        self.db_port = "5432"
    
    def check_postgresql_installation(self) -> bool:
        """Verifica se PostgreSQL está instalado."""
        logger.info("🔍 Verificando instalação do PostgreSQL...")
        
        try:
            # Tentar executar psql --version
            result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"✅ PostgreSQL encontrado: {version}")
                return True
            else:
                logger.error("❌ PostgreSQL não encontrado no PATH")
                return False
        except FileNotFoundError:
            logger.error("❌ PostgreSQL não está instalado ou não está no PATH")
            return False
    
    def create_database_and_user(self) -> bool:
        """Cria banco de dados e usuário."""
        logger.info("🏗️ Criando banco de dados e usuário...")
        
        # SQL commands para criar DB e usuário
        sql_commands = f"""
-- Criar banco de dados
CREATE DATABASE {self.db_name};

-- Criar usuário
CREATE USER {self.db_user} WITH PASSWORD '{self.db_password}';

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user};

-- Conceder privilégios no schema public
\\c {self.db_name}
GRANT ALL ON SCHEMA public TO {self.db_user};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {self.db_user};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {self.db_user};

-- Configurar privilégios padrão para futuras tabelas
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {self.db_user};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {self.db_user};
"""
        
        try:
            # Salvar comandos em arquivo temporário
            temp_sql_file = Path("temp_setup.sql")
            temp_sql_file.write_text(sql_commands)
            
            logger.info("📝 Executando comandos SQL...")
            logger.info("💡 IMPORTANTE: Digite a senha do usuário 'postgres' quando solicitado")
            
            # Executar comandos via psql
            result = subprocess.run([
                'psql', 
                '-U', 'postgres',
                '-h', self.db_host,
                '-p', self.db_port,
                '-f', str(temp_sql_file)
            ], capture_output=True, text=True)
            
            # Remover arquivo temporário
            temp_sql_file.unlink()
            
            if result.returncode == 0:
                logger.info("✅ Banco de dados e usuário criados com sucesso!")
                logger.info(f"📊 Banco: {self.db_name}")
                logger.info(f"👤 Usuário: {self.db_user}")
                return True
            else:
                logger.error(f"❌ Erro ao criar banco: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Testa conexão com o banco criado."""
        logger.info("🔍 Testando conexão com banco criado...")
        
        try:
            # Testar conexão usando psql
            result = subprocess.run([
                'psql',
                '-U', self.db_user,
                '-h', self.db_host,
                '-p', self.db_port,
                '-d', self.db_name,
                '-c', 'SELECT version();'
            ], capture_output=True, text=True, env={**os.environ, 'PGPASSWORD': self.db_password})
            
            if result.returncode == 0:
                logger.info("✅ Conexão com banco de dados bem-sucedida!")
                logger.info(f"📊 Versão: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"❌ Erro na conexão: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar conexão: {e}")
            return False
    
    def update_env_file(self) -> bool:
        """Atualiza arquivo .env com configurações do PostgreSQL."""
        logger.info("⚙️ Atualizando arquivo .env...")
        
        try:
            env_file = Path(".env")
            
            # Configurações do PostgreSQL
            postgres_config = f"""
# PostgreSQL Configuration
DB_HOST={self.db_host}
DB_PORT={self.db_port}
DB_NAME={self.db_name}
DB_USER={self.db_user}
DB_PASSWORD={self.db_password}
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=dev-secret-key-change-in-production

# FBRef Settings
FBREF_BASE_URL=https://fbref.com
FBREF_DELAY_MIN=1.0
FBREF_DELAY_MAX=3.0

# Monitoring
ENABLE_DB_MONITORING=true
METRICS_COLLECTION_INTERVAL=300
"""
            
            env_file.write_text(postgres_config.strip())
            logger.info("✅ Arquivo .env atualizado com configurações PostgreSQL")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar .env: {e}")
            return False
    
    def provide_instructions(self):
        """Fornece instruções caso a configuração automática falhe."""
        logger.info("\n" + "=" * 60)
        logger.info("📋 INSTRUÇÕES MANUAIS PARA POSTGRESQL")
        logger.info("=" * 60)
        
        instructions = f"""
🔧 CASO A CONFIGURAÇÃO AUTOMÁTICA FALHE:

1. INSTALAR POSTGRESQL:
   Windows: https://www.postgresql.org/download/windows/
   - Baixe PostgreSQL 14+ 
   - Durante instalação, anote senha do 'postgres'
   - Mantenha porta padrão 5432

2. CONFIGURAR MANUALMENTE:
   Abra pgAdmin ou psql como 'postgres' e execute:
   
   CREATE DATABASE {self.db_name};
   CREATE USER {self.db_user} WITH PASSWORD '{self.db_password}';
   GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user};
   
   \\c {self.db_name}
   GRANT ALL ON SCHEMA public TO {self.db_user};

3. TESTAR CONEXÃO:
   psql -U {self.db_user} -h {self.db_host} -d {self.db_name}

4. CONTINUAR MIGRAÇÃO:
   python migrate_to_postgresql.py
        """
        
        for line in instructions.strip().split('\n'):
            logger.info(line)
        
        logger.info("=" * 60)
    
    def run_setup(self) -> bool:
        """Executa configuração completa do PostgreSQL."""
        logger.info("🚀 INICIANDO CONFIGURAÇÃO DO POSTGRESQL")
        logger.info("=" * 50)
        
        # Verificar instalação
        if not self.check_postgresql_installation():
            logger.error("❌ PostgreSQL não encontrado!")
            self.provide_instructions()
            return False
        
        # Criar banco e usuário
        if not self.create_database_and_user():
            logger.error("❌ Falha na criação do banco!")
            self.provide_instructions()
            return False
        
        # Testar conexão
        if not self.test_connection():
            logger.error("❌ Falha no teste de conexão!")
            return False
        
        # Atualizar .env
        if not self.update_env_file():
            logger.error("❌ Falha na atualização do .env!")
            return False
        
        logger.info("\n" + "=" * 50)
        logger.info("🎉 POSTGRESQL CONFIGURADO COM SUCESSO!")
        logger.info("=" * 50)
        
        logger.info(f"📊 Banco: {self.db_name}")
        logger.info(f"👤 Usuário: {self.db_user}")
        logger.info(f"🔗 Host: {self.db_host}:{self.db_port}")
        logger.info("✅ Arquivo .env atualizado")
        
        logger.info("\n📋 PRÓXIMOS PASSOS:")
        logger.info("1. python migrate_to_postgresql.py")
        logger.info("2. python teste_sistema_orm.py")
        
        return True

def main():
    """Função principal."""
    print("🚀 CONFIGURAÇÃO AUTOMÁTICA DO POSTGRESQL")
    print("=" * 45)
    
    setup = PostgreSQLSetup()
    
    try:
        success = setup.run_setup()
        
        if success:
            print("\n✅ CONFIGURAÇÃO CONCLUÍDA!")
        else:
            print("\n❌ CONFIGURAÇÃO FALHOU!")
            print("📋 Consulte as instruções manuais acima")
            
    except KeyboardInterrupt:
        print("\n⚠️ Configuração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
