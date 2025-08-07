"""
CONFIGURAÇÃO CENTRALIZADA DO BANCO DE DADOS
==========================================

Sistema de configuração para PostgreSQL com SQLAlchemy e pool de conexões.
Substitui as conexões SQLite hardcoded por configuração centralizada e segura.

Autor: Sistema de Migração de Banco de Dados
Data: 2025-08-03
Versão: 1.0
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseSettings(BaseSettings):
    """Configurações do banco de dados com validação."""
    
    # PostgreSQL Configuration
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="apostapro_db", env="DB_NAME")
    db_user: str = Field(default="apostapro_user", env="DB_USER")
    db_password: str = Field(default="apostapro_pass", env="DB_PASSWORD")
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Connection Pool Settings
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    # Application Settings
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Monitoring
    enable_monitoring: bool = Field(default=True, env="ENABLE_DB_MONITORING")
    metrics_interval: int = Field(default=300, env="METRICS_COLLECTION_INTERVAL")
    
    @validator('database_url', pre=True, always=True)
    def build_database_url(cls, v, values):
        """Constrói a URL do banco se não fornecida."""
        if v:
            return v
        
        return (
            f"postgresql://{values.get('db_user')}:{values.get('db_password')}"
            f"@{values.get('db_host')}:{values.get('db_port')}/{values.get('db_name')}"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignorar campos extras do .env

class DatabaseManager:
    """Gerenciador centralizado de conexões do banco de dados."""
    
    def __init__(self):
        self.settings = DatabaseSettings()
        self.logger = logging.getLogger(__name__)
        self.using_fallback = False
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._base = declarative_base()
        self._metadata = MetaData()
        
        self.logger.info("DatabaseManager inicializado")
        
        # Criar engine e session factory
        self._create_engine()
        self._create_session_factory()
        
        # Configurar logging
        logging.basicConfig(level=getattr(logging, self.settings.log_level))
        logger.info("DatabaseManager inicializado")
    
    @property
    def engine(self) -> Engine:
        """Retorna o engine do SQLAlchemy com pool de conexões."""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Retorna a factory de sessões."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False
            )
        return self._session_factory
    
    @property
    def base(self):
        """Retorna a base declarativa para modelos."""
        return self._base
    
    @property
    def metadata(self) -> MetaData:
        """Retorna os metadados do banco."""
        return self._metadata
    
    def _create_engine(self) -> Engine:
        """Cria o engine do SQLAlchemy com configurações otimizadas."""
        logger.info(f"Criando engine para: {self._mask_password(self.settings.database_url)}")
        
        engine = create_engine(
            self.settings.database_url,
            # Pool de conexões
            poolclass=QueuePool,
            pool_size=self.settings.pool_size,
            max_overflow=self.settings.max_overflow,
            pool_timeout=self.settings.pool_timeout,
            pool_recycle=self.settings.pool_recycle,
            pool_pre_ping=True,  # Verifica conexões antes de usar
            
            # Configurações de performance
            echo=self.settings.debug,  # Log SQL queries em debug
            echo_pool=self.settings.debug,  # Log pool events em debug
            future=True,  # SQLAlchemy 2.0 style
            
            # Configurações de conexão
            connect_args={
                "connect_timeout": 10,
                "application_name": "ApostaPro_FBRef_Scraper",
                "options": "-c timezone=America/Sao_Paulo"
            }
        )
        
        logger.info("Engine criado com sucesso")
        return engine
    
    def _create_session_factory(self):
        """Cria a factory de sessões."""
        self._session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False
        )
    
    def get_session(self):
        """Retorna uma nova sessão do banco de dados."""
        return self.session_factory()
    
    def create_all_tables(self):
        """Cria todas as tabelas definidas nos modelos."""
        logger.info("Criando todas as tabelas...")
        self._base.metadata.create_all(bind=self.engine)
        logger.info("Tabelas criadas com sucesso")
    
    def drop_all_tables(self):
        """Remove todas as tabelas (CUIDADO!)."""
        if self.settings.environment == "production":
            raise ValueError("Não é possível dropar tabelas em produção!")
        
        logger.warning("Removendo todas as tabelas...")
        self._base.metadata.drop_all(bind=self.engine)
        logger.warning("Tabelas removidas")
    
    def test_connection(self) -> bool:
        """Testa a conexão com o banco de dados."""
        try:
            from sqlalchemy import text
            
            with self.engine.connect() as conn:
                # Teste básico de conexão
                result = conn.execute(text("SELECT 1"))
                
                # Tentar obter versão (funciona tanto para PostgreSQL quanto SQLite)
                try:
                    version_result = conn.execute(text("SELECT version()"))
                    version = version_result.fetchone()[0]
                    logger.info(f"✅ Conexão com PostgreSQL bem-sucedida!")
                    logger.info(f"📊 Versão: {version}")
                except:
                    # Fallback para SQLite
                    version_result = conn.execute(text("SELECT sqlite_version()"))
                    version = version_result.fetchone()[0]
                    logger.info(f"✅ Conexão com SQLite bem-sucedida!")
                    logger.info(f"📊 Versão SQLite: {version}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro na conexão com o banco: {e}")
            return False
    
    def get_pool_status(self) -> dict:
        """Retorna o status do pool de conexões."""
        if self._engine is None:
            return {"status": "Engine não inicializado"}
        
        try:
            pool = self._engine.pool
            status = {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow()
            }
            
            # Tentar obter invalid() se existir
            try:
                status["invalid"] = pool.invalid()
            except AttributeError:
                status["invalid"] = "N/A"
            
            return status
        except Exception as e:
            return {"status": f"Erro ao obter status: {e}"}
    
    def close_all_connections(self):
        """Fecha todas as conexões do pool."""
        if self._engine:
            self._engine.dispose()
            logger.info("Todas as conexões fechadas")
    
    def _mask_password(self, url: str) -> str:
        """Mascara a senha na URL para logs."""
        if "://" not in url:
            return url
        
        protocol, rest = url.split("://", 1)
        if "@" not in rest:
            return url
        
        credentials, host_part = rest.split("@", 1)
        if ":" in credentials:
            user, _ = credentials.split(":", 1)
            return f"{protocol}://{user}:***@{host_part}"
        
        return url

# Instância global do gerenciador de banco
db_manager = DatabaseManager()

# Aliases para compatibilidade
engine = db_manager.engine
SessionLocal = db_manager.session_factory
Base = db_manager.base

def get_db():
    """
    Dependency para obter sessão do banco de dados.
    Uso: session = next(get_db())
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Inicializa o banco de dados."""
    logger.info("🚀 Inicializando banco de dados...")
    
    # Testar conexão
    if not db_manager.test_connection():
        raise ConnectionError("Não foi possível conectar ao banco de dados")
    
    # Criar tabelas
    db_manager.create_all_tables()
    
    logger.info("✅ Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    # Teste da configuração
    print("🔍 TESTE DE CONFIGURAÇÃO DO BANCO DE DADOS")
    print("=" * 50)
    
    print(f"📊 Configurações:")
    print(f"  Host: {db_manager.settings.db_host}")
    print(f"  Porta: {db_manager.settings.db_port}")
    print(f"  Banco: {db_manager.settings.db_name}")
    print(f"  Usuário: {db_manager.settings.db_user}")
    print(f"  Pool Size: {db_manager.settings.pool_size}")
    print(f"  Environment: {db_manager.settings.environment}")
    
    print(f"\n🔗 Testando conexão...")
    success = db_manager.test_connection()
    
    if success:
        print("✅ Configuração válida!")
        pool_status = db_manager.get_pool_status()
        print(f"📊 Status do pool: {pool_status}")
    else:
        print("❌ Erro na configuração!")
