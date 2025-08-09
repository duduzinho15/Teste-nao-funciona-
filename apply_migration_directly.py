#!/usr/bin/env python3
"""
Script para aplicar diretamente a migração da tabela posts_redes_sociais
"""
import psycopg2
from psycopg2 import sql
import os

# Configurações de conexão - usando as credenciais identificadas
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'apostapro_db',
    'user': 'apostapro_user',
    'password': 'senha_segura_123'
}

def get_connection():
    """Estabelece conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

def table_exists(conn, table_name):
    """Verifica se uma tabela existe no banco de dados"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            return cur.fetchone()[0]
    except Exception as e:
        print(f"❌ Erro ao verificar se a tabela {table_name} existe: {e}")
        return False

def create_posts_redes_sociais_table(conn):
    """Cria a tabela posts_redes_sociais se não existir"""
    if table_exists(conn, 'posts_redes_sociais'):
        print("✅ A tabela 'posts_redes_sociais' já existe.")
        return True
    
    print("🔧 Criando a tabela 'posts_redes_sociais'...")
    
    try:
        with conn.cursor() as cur:
            # Verifica se a tabela clubes existe (para a chave estrangeira)
            if not table_exists(conn, 'clubes'):
                print("❌ A tabela 'clubes' não existe. Não é possível criar a chave estrangeira.")
                print("   Criando a tabela sem a restrição de chave estrangeira...")
                
                # Cria a tabela sem a restrição de chave estrangeira
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS posts_redes_sociais (
                        id SERIAL PRIMARY KEY,
                        clube_id INTEGER NOT NULL,
                        rede_social VARCHAR(50) NOT NULL,
                        post_id VARCHAR(100) NOT NULL,
                        conteudo TEXT NOT NULL,
                        data_postagem TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                        curtidas INTEGER NOT NULL DEFAULT 0,
                        comentarios INTEGER NOT NULL DEFAULT 0,
                        compartilhamentos INTEGER NOT NULL DEFAULT 0,
                        url_post TEXT,
                        midia_url TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT uq_post_rede_social_id UNIQUE (rede_social, post_id)
                    );
                """)
            else:
                # Cria a tabela com a restrição de chave estrangeira
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS posts_redes_sociais (
                        id SERIAL PRIMARY KEY,
                        clube_id INTEGER NOT NULL,
                        rede_social VARCHAR(50) NOT NULL,
                        post_id VARCHAR(100) NOT NULL,
                        conteudo TEXT NOT NULL,
                        data_postagem TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                        curtidas INTEGER NOT NULL DEFAULT 0,
                        comentarios INTEGER NOT NULL DEFAULT 0,
                        compartilhamentos INTEGER NOT NULL DEFAULT 0,
                        url_post TEXT,
                        midia_url TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (clube_id) REFERENCES clubes(id) ON DELETE CASCADE,
                        CONSTRAINT uq_post_rede_social_id UNIQUE (rede_social, post_id)
                    );
                """)
            
            # Cria índices para melhorar o desempenho
            print("🔧 Criando índices...")
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_clube 
                ON posts_redes_sociais(clube_id);
                
                CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_data 
                ON posts_redes_sociais(data_postagem);
                
                CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_post_id 
                ON posts_redes_sociais(post_id);
                
                CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_rede 
                ON posts_redes_sociais(rede_social);
            """)
            
            print("✅ Tabela 'posts_redes_sociais' criada com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar a tabela 'posts_redes_sociais': {e}")
        return False

def update_alembic_version(conn, version):
    """Atualiza a versão do Alembic"""
    try:
        with conn.cursor() as cur:
            # Verifica se a tabela alembic_version existe
            if not table_exists(conn, 'alembic_version'):
                print("ℹ️  Criando tabela 'alembic_version'...")
                cur.execute("""
                    CREATE TABLE alembic_version (
                        version_num VARCHAR(32) NOT NULL,
                        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                    );
                """)
            
            # Insere ou atualiza a versão
            cur.execute("""
                INSERT INTO alembic_version (version_num) 
                VALUES (%s)
                ON CONFLICT (version_num) 
                DO UPDATE SET version_num = EXCLUDED.version_num;
            """, (version,))
            
            print(f"✅ Versão do Alembic atualizada para: {version}")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao atualizar a versão do Alembic: {e}")
        return False

def main():
    print("🔧 Aplicando migração direta para a tabela 'posts_redes_sociais'")
    print("=" * 80)
    
    # Conecta ao banco de dados
    conn = get_connection()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados. Verifique as credenciais e tente novamente.")
        return
    
    try:
        # Cria a tabela posts_redes_sociais
        if create_posts_redes_sociais_table(conn):
            # Atualiza a versão do Alembic (opcional)
            # Substitua 'xyz' pelo hash da sua migração, se necessário
            update_alembic_version(conn, "3c958e4a60b7")
            
            print("\n✅ Migração aplicada com sucesso!")
        else:
            print("\n❌ Falha ao aplicar a migração.")
    
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
