"""
Script to fix Alembic version history.
This will update the alembic_version table to point to the correct migration.
"""
import os
import sys
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import the database configuration from the project
from Coleta_de_dados.database.config import DatabaseSettings

def fix_alembic_version():
    # Get database settings
    settings = DatabaseSettings()
    
    # Create SQLAlchemy engine using the settings
    engine = create_engine(settings.database_url)
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if alembic_version table exists
        result = session.execute(
            text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'alembic_version'
            )
            """)
        ).scalar()
        
        if not result:
            print("Creating alembic_version table...")
            session.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
            session.commit()
        
        # Set the current version to our new migration
        print("Setting Alembic version to 20250809_1837...")
        session.execute(text("DELETE FROM alembic_version"))
        session.execute(text("INSERT INTO alembic_version (version_num) VALUES ('20250809_1837')"))
        session.commit()
        
        print("Alembic version successfully updated!")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    fix_alembic_version()
