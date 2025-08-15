"""
Script to reset the database and create necessary tables.
"""
import sys
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text as sql_text
from Coleta_de_dados.database.config import db_manager

def create_tables():
    """Create necessary tables directly using SQLAlchemy."""
    engine = db_manager.engine
    metadata = MetaData()
    
    # Drop all existing tables
    with engine.begin() as conn:
        # Drop tables one by one
        drop_statements = [
            "DROP TABLE IF EXISTS posts_redes_sociais CASCADE",
            "DROP TABLE IF EXISTS alembic_version CASCADE"
        ]
        
        for stmt in drop_statements:
            try:
                conn.execute(sql_text(stmt))
                print(f"✅ Executed: {stmt}")
            except Exception as e:
                print(f"⚠️ Warning executing '{stmt}': {e}")
        
        print("✅ Finished dropping tables")
    
    # Create the posts_redes_sociais table without foreign key constraints first
    with engine.begin() as conn:
        # Split the SQL into individual statements and execute them one by one
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS posts_redes_sociais (
            id SERIAL PRIMARY KEY,
            clube_id INTEGER,
            jogador_id INTEGER,
            rede_social VARCHAR(50) NOT NULL,
            post_id VARCHAR(100) NOT NULL,
            conteudo TEXT,
            url_post TEXT,
            data_postagem TIMESTAMP WITH TIME ZONE,
            curtidas INTEGER DEFAULT 0,
            comentarios INTEGER DEFAULT 0,
            compartilhamentos INTEGER DEFAULT 0,
            visualizacoes INTEGER DEFAULT 0,
            tipo_conteudo VARCHAR(20),
            url_imagem TEXT,
            url_video TEXT,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            CONSTRAINT ck_posts_redes_sociais_owner CHECK (clube_id IS NOT NULL OR jogador_id IS NOT NULL),
            CONSTRAINT uq_post_rede_social UNIQUE (rede_social, post_id)
        )
        """
        
        comments_sql = [
            "COMMENT ON TABLE posts_redes_sociais IS 'Armazena posts de redes sociais de clubes e jogadores'",
            "COMMENT ON COLUMN posts_redes_sociais.clube_id IS 'ID do clube dono do post'",
            "COMMENT ON COLUMN posts_redes_sociais.jogador_id IS 'ID do jogador dono do post'",
            "COMMENT ON COLUMN posts_redes_sociais.rede_social IS 'Plataforma de rede social (ex: ''Twitter'', ''Instagram'', ''Facebook'')'",
            "COMMENT ON COLUMN posts_redes_sociais.post_id IS 'ID único do post na plataforma de origem'",
            "COMMENT ON COLUMN posts_redes_sociais.conteudo IS 'Conteúdo textual do post'",
            "COMMENT ON COLUMN posts_redes_sociais.url_post IS 'URL direta para o post na rede social'",
            "COMMENT ON COLUMN posts_redes_sociais.data_postagem IS 'Data e hora em que o post foi publicado'",
            "COMMENT ON COLUMN posts_redes_sociais.curtidas IS 'Número de curtidas/reactions do post'",
            "COMMENT ON COLUMN posts_redes_sociais.comentarios IS 'Número de comentários no post'",
            "COMMENT ON COLUMN posts_redes_sociais.compartilhamentos IS 'Número de compartilhamentos do post'",
            "COMMENT ON COLUMN posts_redes_sociais.visualizacoes IS 'Número de visualizações do post'",
            "COMMENT ON COLUMN posts_redes_sociais.tipo_conteudo IS 'Tipo de conteúdo (''texto'', ''imagem'', ''video'', ''link'', etc.)'",
            "COMMENT ON COLUMN posts_redes_sociais.url_imagem IS 'URL da imagem em anexo ao post'",
            "COMMENT ON COLUMN posts_redes_sociais.url_video IS 'URL do vídeo em anexo ao post'",
            "COMMENT ON COLUMN posts_redes_sociais.created_at IS 'Data de criação do registro'",
            "COMMENT ON COLUMN posts_redes_sociais.updated_at IS 'Data de atualização do registro'"
        ]
        
        try:
            # Create table
            conn.execute(sql_text(create_table_sql))
            print("✅ Created posts_redes_sociais table")
            
            # Add comments
            for comment in comments_sql:
                conn.execute(sql_text(comment))
            print("✅ Added table and column comments")
            
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            raise
        
        # Add foreign key constraints if the referenced tables exist
        try:
            # Check if clubes table exists
            result = conn.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'clubes'
                );
            """).scalar()
            
            if result:
                conn.execute("""
                    ALTER TABLE posts_redes_sociais 
                    ADD CONSTRAINT fk_posts_redes_sociais_clube 
                    FOREIGN KEY (clube_id) REFERENCES clubes(id) ON DELETE CASCADE;
                """)
                print("✅ Added foreign key constraint for clubes")
            
            # Check if jogadores table exists
            result = conn.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'jogadores'
                );
            """).scalar()
            
            if result:
                conn.execute("""
                    ALTER TABLE posts_redes_sociais 
                    ADD CONSTRAINT fk_posts_redes_sociais_jogador 
                    FOREIGN KEY (jogador_id) REFERENCES jogadores(id) ON DELETE CASCADE;
                """)
                print("✅ Added foreign key constraint for jogadores")
                
        except Exception as e:
            print(f"⚠️ Warning: Could not add foreign key constraints: {e}")
            print("The table was created, but foreign key constraints could not be added.")
            print("This is expected if the referenced tables don't exist yet.")
    
    # Create alembic_version table if it doesn't exist
    with engine.begin() as conn:
        create_alembic_version = """
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) NOT NULL
            )
        """
        try:
            conn.execute(sql_text(create_alembic_version))
            print("✅ Created alembic_version table")
            
            # Insert the current migration version
            version = '20250809_1837_create_posts_redes_sociais_table'  # The latest migration version
            insert_version = "INSERT INTO alembic_version (version_num) VALUES (:version)"
            conn.execute(sql_text(insert_version), {'version': version})
            print(f"✅ Inserted version {version} into alembic_version")
            
        except Exception as e:
            print(f"⚠️ Warning creating alembic_version table: {e}")
            print("This is non-critical and can be ignored if the table already exists.")

if __name__ == "__main__":
    print("🔄 Resetting database and creating tables...")
    try:
        create_tables()
        print("\n✅ Database reset and tables created successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
