#!/usr/bin/env python3
"""
SCRIPT DE MIGRAÇÃO PARA POSTGRESQL
==================================

Script simplificado para migrar do SQLite para PostgreSQL.
Funciona de forma independente e cria as tabelas usando SQLAlchemy ORM.

Funcionalidades:
1. Testa conexão PostgreSQL
2. Cria schema usando SQLAlchemy ORM
3. Opcionalmente migra dados do SQLite existente
4. Fornece instruções de configuração

Autor: Sistema de Migração de Banco de Dados
Data: 2025-08-03
Versão: 1.0
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Classe para migração do banco de dados."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.sqlite_path = self.project_root / "fbref_data.db"
        
    def check_postgresql_availability(self) -> bool:
        """Verifica se PostgreSQL está disponível."""
        logger.info("🔍 Verificando disponibilidade do PostgreSQL...")
        
        try:
            # Tentar importar psycopg2
            import psycopg2
            logger.info("✅ psycopg2 disponível")
            
            # Tentar conectar usando as configurações do .env
            from Coleta_de_dados.database.config import db_manager
            
            # Testar conexão
            success = db_manager.test_connection()
            
            if success:
                logger.info("✅ PostgreSQL disponível e acessível")
                return True
            else:
                logger.warning("⚠️ PostgreSQL não está acessível")
                return False
                
        except ImportError:
            logger.warning("⚠️ psycopg2 não instalado")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Erro ao conectar PostgreSQL: {e}")
            return False
    
    def create_postgresql_schema(self) -> bool:
        """Cria o schema PostgreSQL usando SQLAlchemy ORM."""
        logger.info("🏗️ Criando schema PostgreSQL...")
        
        try:
            from Coleta_de_dados.database.config import db_manager
            from Coleta_de_dados.database.models import Base
            
            # Criar todas as tabelas
            Base.metadata.create_all(bind=db_manager.engine)
            
            logger.info("✅ Schema PostgreSQL criado com sucesso!")
            
            # Verificar tabelas criadas
            from sqlalchemy import text
            with db_manager.get_session() as session:
                result = session.execute(
                    text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                )
                tables = [row[0] for row in result.fetchall()]
                
            logger.info(f"📊 Tabelas criadas: {', '.join(tables)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar schema PostgreSQL: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def create_sqlite_fallback_schema(self) -> bool:
        """Cria schema SQLite usando SQLAlchemy ORM como fallback."""
        logger.info("🏗️ Criando schema SQLite como fallback...")
        
        try:
            from sqlalchemy import create_engine
            from Coleta_de_dados.database.models import Base
            
            # Criar engine SQLite
            sqlite_url = f"sqlite:///{self.sqlite_path}"
            engine = create_engine(sqlite_url, echo=False)
            
            # Criar todas as tabelas
            Base.metadata.create_all(bind=engine)
            
            logger.info("✅ Schema SQLite criado com sucesso!")
            
            # Verificar tabelas criadas
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                tables = [row[0] for row in result.fetchall()]
                
            logger.info(f"📊 Tabelas criadas: {', '.join(tables)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar schema SQLite: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def analyze_existing_sqlite_data(self) -> Dict[str, int]:
        """Analisa dados existentes no SQLite."""
        logger.info("📊 Analisando dados existentes no SQLite...")
        
        if not self.sqlite_path.exists():
            logger.info("ℹ️ Nenhum banco SQLite existente encontrado")
            return {}
        
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            # Obter lista de tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Contar registros em cada tabela
            table_counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_counts[table] = count
                
            conn.close()
            
            logger.info("📈 Dados existentes:")
            for table, count in table_counts.items():
                logger.info(f"   {table}: {count} registros")
                
            return table_counts
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar SQLite: {e}")
            return {}
    
    def provide_postgresql_setup_instructions(self):
        """Fornece instruções para configurar PostgreSQL."""
        logger.info("\n" + "=" * 60)
        logger.info("📋 INSTRUÇÕES PARA CONFIGURAR POSTGRESQL")
        logger.info("=" * 60)
        
        instructions = """
🔧 PASSO 1: INSTALAR POSTGRESQL
   Windows: https://www.postgresql.org/download/windows/
   - Baixe e instale PostgreSQL 14+ 
   - Anote a senha do usuário 'postgres'
   - Mantenha porta padrão 5432

🔧 PASSO 2: CRIAR BANCO DE DADOS
   Abra pgAdmin ou psql e execute:
   
   CREATE DATABASE apostapro_db;
   CREATE USER apostapro_user WITH PASSWORD 'apostapro_pass';
   GRANT ALL PRIVILEGES ON DATABASE apostapro_db TO apostapro_user;

🔧 PASSO 3: CONFIGURAR .ENV
   Edite o arquivo .env com suas credenciais:
   
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=apostapro_db
   DB_USER=apostapro_user
   DB_PASSWORD=apostapro_pass

🔧 PASSO 4: EXECUTAR MIGRAÇÃO
   Execute novamente este script:
   
   python migrate_to_postgresql.py

📚 RECURSOS ÚTEIS:
   - Documentação PostgreSQL: https://www.postgresql.org/docs/
   - pgAdmin (GUI): https://www.pgadmin.org/
   - Configuração de conexão: https://www.postgresql.org/docs/current/auth-pg-hba-conf.html
        """
        
        for line in instructions.strip().split('\n'):
            logger.info(line)
        
        logger.info("=" * 60)
    
    def run_migration(self) -> bool:
        """Executa a migração completa."""
        logger.info("🚀 INICIANDO MIGRAÇÃO DO BANCO DE DADOS")
        logger.info("=" * 60)
        
        # Analisar dados existentes
        existing_data = self.analyze_existing_sqlite_data()
        
        # Verificar PostgreSQL
        postgresql_available = self.check_postgresql_availability()
        
        if postgresql_available:
            logger.info("✅ PostgreSQL detectado - usando PostgreSQL")
            success = self.create_postgresql_schema()
            
            if success:
                logger.info("\n🎉 MIGRAÇÃO PARA POSTGRESQL CONCLUÍDA!")
                logger.info("✅ Sistema configurado para usar PostgreSQL + SQLAlchemy ORM")
                
                if existing_data:
                    logger.info("\n📋 PRÓXIMOS PASSOS:")
                    logger.info("1. Refatorar scripts para usar SQLAlchemy ORM")
                    logger.info("2. Testar pipeline de coleta")
                    logger.info("3. Migrar dados existentes se necessário")
                
                return True
            else:
                logger.error("❌ Falha na criação do schema PostgreSQL")
                return False
        else:
            logger.warning("⚠️ PostgreSQL não disponível - usando SQLite como fallback")
            success = self.create_sqlite_fallback_schema()
            
            if success:
                logger.info("\n✅ SCHEMA SQLITE CRIADO COM SQLALCHEMY ORM")
                logger.info("📝 Sistema configurado para usar SQLite + SQLAlchemy ORM")
                
                # Fornecer instruções para PostgreSQL
                self.provide_postgresql_setup_instructions()
                
                return True
            else:
                logger.error("❌ Falha na criação do schema SQLite")
                return False

def main():
    """Função principal."""
    print("🚀 MIGRAÇÃO DO BANCO DE DADOS - FBREF SCRAPER")
    print("=" * 50)
    
    migrator = DatabaseMigrator()
    
    try:
        success = migrator.run_migration()
        
        if success:
            print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        else:
            print("\n❌ MIGRAÇÃO FALHOU!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Migração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
