#!/usr/bin/env python3
"""
Script para corrigir problemas de encoding e forçar a aplicação de migrações
"""
import psycopg2
import sys
import os
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configurações de conexão
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'apostapro_db',
    'user': 'postgres',  # Usando superusuário para operações administrativas
    'password': 'postgres'  # Senha padrão do PostgreSQL no Windows
}

def get_connection(dbname=None):
    """Estabelece conexão com o banco de dados"""
    params = DB_CONFIG.copy()
    if dbname:
        params['dbname'] = dbname
    
    try:
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

def check_database_encoding(conn):
    """Verifica o encoding do banco de dados"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT datname, pg_encoding_to_char(encoding) FROM pg_database WHERE datname = %s;", 
                       (DB_CONFIG['dbname'],))
            result = cur.fetchone()
            if result:
                db_name, encoding = result
                print(f"✅ Banco de dados '{db_name}' está usando encoding: {encoding}")
                return encoding
            else:
                print(f"❌ Banco de dados '{DB_CONFIG['dbname']}' não encontrado.")
                return None
    except Exception as e:
        print(f"❌ Erro ao verificar encoding: {e}")
        return None

def list_tables(conn):
    """Lista todas as tabelas no esquema público"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cur.fetchall()]
            
            if tables:
                print("\n📋 Tabelas encontradas:")
                for table in tables:
                    print(f"- {table}")
            else:
                print("\nℹ️  Nenhuma tabela encontrada no esquema público.")
            
            return tables
    except Exception as e:
        print(f"❌ Erro ao listar tabelas: {e}")
        return []

def check_alembic_version(conn):
    """Verifica a versão atual do Alembic"""
    try:
        with conn.cursor() as cur:
            # Verifica se a tabela alembic_version existe
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'alembic_version';
            """)
            
            if not cur.fetchone():
                print("\n⚠️  Tabela 'alembic_version' não encontrada.")
                return None
            
            # Obtém a versão atual do Alembic
            cur.execute("SELECT version_num FROM alembic_version;")
            version = cur.fetchone()
            if version:
                version = version[0]
                print(f"\nℹ️  Versão atual do Alembic: {version}")
                return version
            else:
                print("\n⚠️  Não foi possível determinar a versão do Alembic.")
                return None
                
    except Exception as e:
        print(f"❌ Erro ao verificar versão do Alembic: {e}")
        return None

def force_migration():
    """Força a aplicação da migração para a tabela posts_redes_sociais"""
    # Conecta ao banco de dados postgres para poder recriar o banco se necessário
    conn = get_connection('postgres')
    if not conn:
        print("❌ Não foi possível conectar ao servidor PostgreSQL.")
        return False
    
    try:
        with conn.cursor() as cur:
            # Verifica se o banco de dados existe
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['dbname'],))
            db_exists = cur.fetchone() is not None
            
            if not db_exists:
                print(f"\nℹ️  Banco de dados '{DB_CONFIG['dbname']}' não existe. Criando...")
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_CONFIG['dbname'])))
                print(f"✅ Banco de dados '{DB_CONFIG['dbname']}' criado com sucesso!")
    
    except Exception as e:
        print(f"❌ Erro ao verificar/criar banco de dados: {e}")
        return False
    finally:
        conn.close()
    
    # Agora conecta ao banco de dados específico
    conn = get_connection()
    if not conn:
        return False
    
    try:
        # Verifica o encoding do banco de dados
        encoding = check_database_encoding(conn)
        if not encoding or encoding.upper() != 'UTF8':
            print(f"\n⚠️  O banco de dados não está usando UTF-8. Isso pode causar problemas de codificação.")
            print("   Considere recriar o banco de dados com o encoding correto.")
        
        # Lista as tabelas atuais
        current_tables = list_tables(conn)
        
        # Verifica a versão do Alembic
        current_version = check_alembic_version(conn)
        
        # Verifica se a tabela posts_redes_sociais já existe
        if 'posts_redes_sociais' in current_tables:
            print("\n✅ A tabela 'posts_redes_sociais' já existe no banco de dados.")
            return True
            
        # Se chegou aqui, a tabela não existe e precisamos forçar a migração
        print("\n🔧 A tabela 'posts_redes_sociais' não foi encontrada. Forçando a migração...")
        
        # Aqui você pode adicionar o código SQL para criar a tabela manualmente
        # ou executar o comando Alembic para aplicar as migrações
        print("\nPara forçar a migração, execute o seguinte comando no terminal:")
        print(f"cd {os.path.dirname(os.path.abspath(__file__))}")
        print("alembic upgrade head")
        print("\nOu execute o seguinte comando SQL diretamente no banco de dados:")
        print("""
CREATE TABLE IF NOT EXISTS posts_redes_sociais (
    id SERIAL PRIMARY KEY,
    clube_id INTEGER NOT NULL,
    rede_social VARCHAR(50) NOT NULL,
    post_id VARCHAR(100) NOT NULL,
    conteudo TEXT NOT NULL,
    data_postagem TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    curtidas INTEGER NOT NULL,
    comentarios INTEGER NOT NULL,
    compartilhamentos INTEGER NOT NULL,
    url_post TEXT,
    midia_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clube_id) REFERENCES clubes(id) ON DELETE CASCADE,
    CONSTRAINT uq_post_rede_social_id UNIQUE (rede_social, post_id)
);

CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_clube ON posts_redes_sociais(clube_id);
CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_data ON posts_redes_sociais(data_postagem);
CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_post_id ON posts_redes_sociais(post_id);
CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_rede ON posts_redes_sociais(rede_social);
        """)
        
        return False
        
    except Exception as e:
        print(f"❌ Erro ao forçar migração: {e}")
        return False
    finally:
        conn.close()

def main():
    print("🔧 Ferramenta de Correção de Encoding e Migrações")
    print("=" * 60)
    
    # Verifica se o PostgreSQL está rodando
    print("\n🔍 Verificando conexão com o PostgreSQL...")
    conn = get_connection('postgres')
    if not conn:
        print("❌ Não foi possível conectar ao servidor PostgreSQL.")
        print("\nVerifique se o serviço PostgreSQL está em execução e tente novamente.")
        return
    
    print("✅ Conectado ao servidor PostgreSQL com sucesso!")
    conn.close()
    
    # Força a migração
    success = force_migration()
    
    if success:
        print("\n✅ Tarefas concluídas com sucesso!")
    else:
        print("\n⚠️  Algumas tarefas podem não ter sido concluídas com sucesso. Verifique as mensagens acima.")

if __name__ == "__main__":
    main()
