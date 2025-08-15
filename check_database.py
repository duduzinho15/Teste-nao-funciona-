"""
Script para verificar e configurar o banco de dados PostgreSQL.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def main():
    # Configurações de conexão do arquivo .env
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'postgres',  # Banco padrão para criar outros bancos
        'user': 'postgres',
        'password': 'postgres'  # Senha padrão do PostgreSQL no Windows
    }
    
    # String de conexão para o banco padrão
    default_conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    try:
        # Conecta ao banco padrão
        print("🔍 Conectando ao PostgreSQL...")
        engine = create_engine(default_conn_str)
        conn = engine.connect()
        
        # Verifica se o banco de dados existe
        print("🔍 Verificando se o banco de dados 'apostapro_db' existe...")
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'apostapro_db'"))
        db_exists = result.scalar() is not None
        
        if not db_exists:
            print("ℹ️  Banco de dados 'apostapro_db' não encontrado. Criando...")
            conn.execute(text("COMMIT"))  # Encerra qualquer transação ativa
            conn.execute(text("CREATE DATABASE apostapro_db WITH ENCODING='UTF8' LC_COLLATE='pt_BR.UTF-8' LC_CTYPE='pt_BR.UTF-8' TEMPLATE=template0"))
            print("✅ Banco de dados 'apostapro_db' criado com sucesso!")
        else:
            print("✅ Banco de dados 'apostapro_db' já existe.")
        
        # Verifica se o usuário existe
        print("\n🔍 Verificando se o usuário 'apostapro_user' existe...")
        result = conn.execute(text("SELECT 1 FROM pg_roles WHERE rolname = 'apostapro_user'"))
        user_exists = result.scalar() is not None
        
        if not user_exists:
            print("ℹ️  Usuário 'apostapro_user' não encontrado. Criando...")
            conn.execute(text("CREATE USER apostapro_user WITH PASSWORD 'senha_segura_123'"))
            print("✅ Usuário 'apostapro_user' criado com sucesso!")
        else:
            print("✅ Usuário 'apostapro_user' já existe.")
        
        # Concede privilégios
        print("\n🔑 Concedendo privilégios ao usuário...")
        conn.execute(text("GRANT ALL PRIVILEGES ON DATABASE apostapro_db TO apostapro_user"))
        conn.execute(text("ALTER DATABASE apostapro_db OWNER TO apostapro_user"))
        print("✅ Privilégios concedidos com sucesso!")
        
        # Verifica a conexão com o banco de dados
        print("\n🔍 Testando conexão com o banco de dados 'apostapro_db'...")
        test_conn_str = f"postgresql://apostapro_user:senha_segura_123@{db_config['host']}:{db_config['port']}/apostapro_db"
        test_engine = create_engine(test_conn_str)
        
        try:
            with test_engine.connect() as test_conn:
                test_conn.execute(text("SELECT 1"))
            print("✅ Conexão com o banco de dados 'apostapro_db' bem-sucedida!")
        except Exception as e:
            print(f"❌ Falha ao conectar ao banco de dados 'apostapro_db': {e}")
            return 1
        
        print("\n✅ Configuração do banco de dados concluída com sucesso!")
        return 0
        
    except Exception as e:
        print(f"❌ Erro durante a configuração do banco de dados: {e}")
        return 1
    finally:
        if 'conn' in locals():
            conn.close()
        if 'engine' in locals():
            engine.dispose()
        if 'test_engine' in locals():
            test_engine.dispose()

if __name__ == "__main__":
    sys.exit(main())
