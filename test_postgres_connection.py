import psycopg2
import os
import sys
from urllib.parse import urlparse

def test_connection(host, port, dbname, user, password):
    """Testa a conexão com o PostgreSQL"""
    print(f"\n{'='*60}")
    print(f"Testando conexão com: {user}@{host}:{port}/{dbname}")
    print(f"{'='*60}")
    
    # Teste 1: Conexão direta
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        print("✅ Conexão direta bem-sucedida!")
        
        # Listar tabelas
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
                
            # Verificar tabela alembic_version
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'alembic_version';
            """)
            if cur.fetchone():
                cur.execute("SELECT version_num FROM alembic_version;")
                version = cur.fetchone()[0]
                print(f"\nℹ️  Versão do Alembic: {version}")
            else:
                print("\n⚠️  Tabela alembic_version não encontrada.")
                
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão direta: {str(e).strip()}")
        return False

def main():
    # Configurações de conexão
    configs = [
        # PostgreSQL padrão
        {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'postgres',
            'user': 'postgres',
            'password': 'postgres'
        },
        # Configuração do projeto
        {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'apostapro_db',
            'user': 'apostapro_user',
            'password': 'senha_segura_123'
        },
        # Banco de teste
        {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'test_db',
            'user': 'postgres',
            'password': 'postgres'
        }
    ]
    
    print("🔍 Iniciando testes de conexão com o PostgreSQL...\n")
    
    # Testar cada configuração
    for config in configs:
        test_connection(**config)
    
    print("\n✅ Testes de conexão concluídos!")

if __name__ == "__main__":
    main()
