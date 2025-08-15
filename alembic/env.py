"""
ALEMBIC ENVIRONMENT - CONFIGURAÇÃO DE MIGRATIONS
===============================================

Configuração do ambiente Alembic para migrations do banco PostgreSQL.
Integrado com SQLAlchemy e configurações centralizadas.

Autor: Sistema de Migração de Banco de Dados
Data: 2025-08-03
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importar configurações e modelos
try:
    from Coleta_de_dados.database.config import db_manager
    from Coleta_de_dados.database.models import Base
    target_metadata = Base.metadata
except ImportError:
    # Fallback se não conseguir importar os modelos
    from sqlalchemy import MetaData
    target_metadata = MetaData()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url():
    """Obtém a URL do banco de dados das configurações."""
    try:
        if db_manager and hasattr(db_manager, 'settings'):
            return db_manager.settings.database_url
    except:
        pass
    
    # Fallback para SQLite
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Banco_de_dados", "aposta.db")
    return f"sqlite:///{db_path}"

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    try:
        # Tentar usar o engine configurado
        if db_manager and hasattr(db_manager, 'engine') and db_manager.engine:
            connectable = db_manager.engine
        else:
            # Fallback: criar engine diretamente
            from sqlalchemy import create_engine
            url = get_url()
            connectable = create_engine(url)
    except Exception as e:
        # Fallback final: criar engine SQLite
        from sqlalchemy import create_engine
        import os
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Banco_de_dados", "aposta.db")
        url = f"sqlite:///{db_path}"
        connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,  # SQLite requer batch mode
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
