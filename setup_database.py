#!/usr/bin/env python3
"""
SCRIPT DE CONFIGURAÇÃO DO BANCO DE DADOS
========================================

Script para configurar e migrar o banco de dados do SQLite para PostgreSQL.
Inclui instalação de dependências, configuração inicial e primeira migração.

Funcionalidades:
1. Instalar dependências do PostgreSQL
2. Configurar banco de dados PostgreSQL
3. Executar primeira migração com Alembic
4. Validar configuração
5. Migrar dados existentes (opcional)

Autor: Sistema de Migração de Banco de Dados
Data: 2025-08-03
Versão: 1.0
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Classe para configuração do banco de dados."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements_database.txt"
        self.env_file = self.project_root / ".env"
        self.env_template = self.project_root / ".env.template"
        
    def install_dependencies(self) -> bool:
        """Instala as dependências do banco de dados."""
        logger.info("🔧 Instalando dependências do banco de dados...")
        
        try:
            # Verificar se o arquivo de requirements existe
            if not self.requirements_file.exists():
                logger.error(f"❌ Arquivo de requirements não encontrado: {self.requirements_file}")
                return False
            
            # Instalar dependências
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Dependências instaladas com sucesso!")
                return True
            else:
                logger.error(f"❌ Erro ao instalar dependências: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao instalar dependências: {e}")
            return False
    
    def setup_environment(self) -> bool:
        """Configura o arquivo de ambiente."""
        logger.info("⚙️ Configurando arquivo de ambiente...")
        
        try:
            # Verificar se .env já existe
            if self.env_file.exists():
                logger.info("ℹ️ Arquivo .env já existe, mantendo configurações atuais")
                return True
            
            # Verificar se template existe
            if not self.env_template.exists():
                logger.error(f"❌ Template .env não encontrado: {self.env_template}")
                return False
            
            # Copiar template para .env
            import shutil
            shutil.copy2(self.env_template, self.env_file)
            
            logger.info("✅ Arquivo .env criado a partir do template")
            logger.warning("⚠️ IMPORTANTE: Configure as credenciais do PostgreSQL no arquivo .env")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar ambiente: {e}")
            return False
    
    def test_database_connection(self) -> bool:
        """Testa a conexão com o banco de dados."""
        logger.info("🔍 Testando conexão com o banco de dados...")
        
        try:
            # Importar após instalar dependências
            sys.path.insert(0, str(self.project_root))
            from Coleta_de_dados.database.config import db_manager
            
            # Testar conexão
            success = db_manager.test_connection()
            
            if success:
                logger.info("✅ Conexão com PostgreSQL estabelecida!")
                
                # Mostrar status do pool
                pool_status = db_manager.get_pool_status()
                logger.info(f"📊 Status do pool: {pool_status}")
                
                return True
            else:
                logger.error("❌ Falha na conexão com PostgreSQL")
                logger.error("💡 Verifique se:")
                logger.error("   - PostgreSQL está instalado e rodando")
                logger.error("   - Credenciais no .env estão corretas")
                logger.error("   - Banco de dados existe")
                return False
                
        except ImportError as e:
            logger.error(f"❌ Erro ao importar módulos: {e}")
            logger.error("💡 Execute primeiro: pip install -r requirements_database.txt")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao testar conexão: {e}")
            return False
    
    def initialize_alembic(self) -> bool:
        """Inicializa o Alembic se necessário."""
        logger.info("🗂️ Inicializando sistema de migrations...")
        
        try:
            alembic_dir = self.project_root / "alembic"
            versions_dir = alembic_dir / "versions"
            
            # Criar diretório versions se não existir
            versions_dir.mkdir(parents=True, exist_ok=True)
            
            # Verificar se já existe alguma migration
            if any(versions_dir.glob("*.py")):
                logger.info("ℹ️ Migrations já existem, pulando inicialização")
                return True
            
            logger.info("✅ Diretório de migrations configurado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Alembic: {e}")
            return False
    
    def create_initial_migration(self) -> bool:
        """Cria a migração inicial do schema."""
        logger.info("📝 Criando migração inicial do schema...")
        
        try:
            # Executar alembic revision --autogenerate
            cmd = [
                sys.executable, "-m", "alembic", "revision", 
                "--autogenerate", "-m", "Initial schema migration"
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Migração inicial criada com sucesso!")
                logger.info(f"📄 Output: {result.stdout}")
                return True
            else:
                logger.error(f"❌ Erro ao criar migração: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao criar migração: {e}")
            return False
    
    def run_migrations(self) -> bool:
        """Executa as migrations no banco de dados."""
        logger.info("🚀 Executando migrations no banco de dados...")
        
        try:
            # Executar alembic upgrade head
            cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Migrations executadas com sucesso!")
                logger.info(f"📄 Output: {result.stdout}")
                return True
            else:
                logger.error(f"❌ Erro ao executar migrations: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao executar migrations: {e}")
            return False
    
    def validate_schema(self) -> bool:
        """Valida se o schema foi criado corretamente."""
        logger.info("✅ Validando schema do banco de dados...")
        
        try:
            sys.path.insert(0, str(self.project_root))
            from Coleta_de_dados.database.config import db_manager
            
            # Testar criação de uma sessão
            session = db_manager.get_session()
            
            # Verificar se consegue fazer uma query simples
            result = session.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = result.scalar()
            
            session.close()
            
            logger.info(f"✅ Schema validado! {table_count} tabelas encontradas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao validar schema: {e}")
            return False
    
    def run_full_setup(self) -> bool:
        """Executa a configuração completa do banco de dados."""
        logger.info("🚀 INICIANDO CONFIGURAÇÃO COMPLETA DO BANCO DE DADOS")
        logger.info("=" * 60)
        
        steps = [
            ("Instalação de dependências", self.install_dependencies),
            ("Configuração de ambiente", self.setup_environment),
            ("Teste de conexão", self.test_database_connection),
            ("Inicialização do Alembic", self.initialize_alembic),
            ("Criação da migração inicial", self.create_initial_migration),
            ("Execução das migrations", self.run_migrations),
            ("Validação do schema", self.validate_schema),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n🔄 {step_name}...")
            
            if not step_func():
                logger.error(f"❌ FALHA em: {step_name}")
                logger.error("🛑 Configuração interrompida")
                return False
            
            logger.info(f"✅ {step_name} concluída")
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 CONFIGURAÇÃO DO BANCO DE DADOS CONCLUÍDA COM SUCESSO!")
        logger.info("=" * 60)
        
        logger.info("\n📋 PRÓXIMOS PASSOS:")
        logger.info("1. Refatorar scripts para usar SQLAlchemy ORM")
        logger.info("2. Remover dependências do SQLite")
        logger.info("3. Testar pipeline de coleta completo")
        logger.info("4. Migrar dados existentes se necessário")
        
        return True

def main():
    """Função principal."""
    print("🚀 CONFIGURAÇÃO DO BANCO DE DADOS POSTGRESQL")
    print("=" * 50)
    
    setup = DatabaseSetup()
    
    try:
        success = setup.run_full_setup()
        
        if success:
            print("\n✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
            print("🎯 Sistema pronto para usar PostgreSQL + SQLAlchemy")
        else:
            print("\n❌ CONFIGURAÇÃO FALHOU!")
            print("🔧 Verifique os logs acima para detalhes")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Configuração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
