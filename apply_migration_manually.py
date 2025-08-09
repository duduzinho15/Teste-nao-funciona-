"""
APLICAÇÃO MANUAL DE MIGRAÇÃO
===========================

Script para aplicar manualmente a migração da tabela posts_redes_sociais.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

def apply_migration():
    """Aplica manualmente a migração para criar a tabela posts_redes_sociais."""
    print(f"🔍 Conectando ao banco de dados: {DB_URL.replace(os.getenv('DB_PASSWORD'), '***')}")
    
    try:
        # Cria uma conexão com o banco de dados
        engine = create_engine(DB_URL)
        conn = engine.connect()
        
        # Verifica se a tabela já existe
        result = conn.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'posts_redes_sociais')")
        )
        table_exists = result.scalar()
        
        if table_exists:
            print("✅ A tabela 'posts_redes_sociais' já existe no banco de dados.")
            return
            
        print("🚀 Aplicando migração para criar a tabela 'posts_redes_sociais'...")
        
        # Desativa temporariamente as verificações de chave estrangeira
        conn.execute(text("SET CONSTRAINTS ALL DEFERRED"))
        
        # Cria a tabela
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS posts_redes_sociais (
                    id SERIAL PRIMARY KEY,
                    clube_id INTEGER NOT NULL,
                    rede_social VARCHAR(50) NOT NULL,
                    post_id VARCHAR(100) NOT NULL,
                    conteudo TEXT NOT NULL,
                    data_postagem TIMESTAMP WITH TIME ZONE NOT NULL,
                    curtidas INTEGER NOT NULL DEFAULT 0,
                    comentarios INTEGER NOT NULL DEFAULT 0,
                    compartilhamentos INTEGER NOT NULL DEFAULT 0,
                    url_post TEXT,
                    midia_url TEXT,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    CONSTRAINT fk_clube
                        FOREIGN KEY (clube_id) 
                        REFERENCES clubes (id)
                        ON DELETE CASCADE,
                    CONSTRAINT ck_posts_rede_social_valida
                        CHECK (rede_social IN ('Twitter', 'Instagram', 'Facebook', 'YouTube', 'TikTok', 'Outro')),
                    CONSTRAINT uq_post_rede_social_id UNIQUE (post_id)
                )
            """))
            print("✅ Tabela 'posts_redes_sociais' criada com sucesso!")
        except Exception as e:
            print(f"ℹ️ Aviso ao criar a tabela: {e}")
        
        # Cria índices apenas se não existirem
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_clube ON posts_redes_sociais (clube_id);
                CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_data ON posts_redes_sociais (data_postagem);
                CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_rede ON posts_redes_sociais (rede_social);
                CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_engajamento ON posts_redes_sociais (curtidas, comentarios, compartilhamentos);
            """))
            print("✅ Índices criados com sucesso!")
        except Exception as e:
            print(f"ℹ️ Aviso ao criar índices: {e}")
            
            print("✅ Tabela 'posts_redes_sociais' criada com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao aplicar a migração: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    apply_migration()
