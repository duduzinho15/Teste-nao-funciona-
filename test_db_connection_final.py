import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError

def test_db_connection():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Obtém as configurações do banco de dados
    db_config = {
        'dbname': os.getenv('DB_NAME', 'apostapro_db'),
        'user': os.getenv('DB_USER', 'apostapro_user'),
        'password': os.getenv('DB_PASSWORD', 'apostapro_pass'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    print("🔍 Testando conexão com o banco de dados...")
    print(f"📋 Configurações:")
    for key, value in db_config.items():
        print(f"   {key.upper()}: {value}")
    
    try:
        # Tenta estabelecer uma conexão
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Executa uma consulta simples para verificar a conexão
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print(f"\n✅ Conexão bem-sucedida!")
        print(f"   Versão do PostgreSQL: {db_version[0]}")
        
        # Verifica se o banco de dados existe e está acessível
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"   Banco de dados atual: {db_info[0]}")
        print(f"   Usuário atual: {db_info[1]}")
        
        # Lista as tabelas existentes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 Tabelas no banco de dados ({len(tables)}):")
        for i, table in enumerate(tables, 1):
            print(f"   {i}. {table[0]}")
        
        # Fecha a conexão
        cursor.close()
        conn.close()
        return True
        
    except OperationalError as e:
        print(f"\n❌ Falha na conexão com o banco de dados:")
        print(f"   Erro: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Script de teste de conexão com o banco de dados")
    print("=" * 60)
    
    # Verifica se o módulo psycopg2 está instalado
    try:
        import psycopg2
    except ImportError:
        print("\n❌ O módulo 'psycopg2' não está instalado.")
        print("   Instale-o com: pip install psycopg2-binary")
        sys.exit(1)
    
    # Executa o teste de conexão
    success = test_db_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Teste concluído com sucesso!")
    else:
        print("❌ Ocorreram erros durante o teste de conexão.")
        print("   Verifique as configurações no arquivo .env e certifique-se de que o PostgreSQL está rodando.")
    
    sys.exit(0 if success else 1)
