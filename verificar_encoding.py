import psycopg2
import sys
from getpass import getpass

def test_connection(host, port, dbname, user, password):
    try:
        # Forçar codificação UTF-8
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            client_encoding='UTF8'
        )
        
        with conn.cursor() as cur:
            # Verificar encoding do banco de dados
            print("\n🔍 Verificando encoding dos bancos de dados...")
            cur.execute("SELECT datname, pg_encoding_to_char(encoding) FROM pg_database;")
            print("\n🔤 Encoding dos bancos de dados:")
            for db in cur.fetchall():
                print(f" - {db[0]}: {db[1]}")
            
            # Verificar collation
            print("\n🔡 Verificando collation do banco 'apostapro_db'...")
            cur.execute("""
                SELECT datname, datcollate, datctype 
                FROM pg_database 
                WHERE datname = 'apostapro_db';
            """)
            collation = cur.fetchone()
            if collation:
                print("\n📝 Informações de Collation:")
                print(f" - Banco: {collation[0]}")
                print(f" - Collate: {collation[1]}")
                print(f" - Ctype: {collation[2]}")
            else:
                print("⚠️  Banco de dados 'apostapro_db' não encontrado!")
            
            # Verificar configurações do servidor
            print("\n⚙️  Configurações do servidor:")
            try:
                cur.execute("SHOW server_encoding;")
                print(f" - Server Encoding: {cur.fetchone()[0]}")
                
                cur.execute("SHOW client_encoding;")
                print(f" - Client Encoding: {cur.fetchone()[0]}")
                
                cur.execute("SHOW lc_collate;")
                print(f" - LC_COLLATE: {cur.fetchone()[0]}")
                
                cur.execute("SHOW lc_ctype;")
                print(f" - LC_CTYPE: {cur.fetchone()[0]}")
                
            except Exception as e:
                print(f"⚠️  Não foi possível verificar todas as configurações: {e}")
            
        conn.close()
        return True
        
    except Exception as e:
        error_msg = str(e).encode('ascii', 'replace').decode('ascii')
        print(f"\n❌ Erro ao conectar: {error_msg}")
        
        # Tentar diagnosticar o erro
        if "password authentication failed" in str(e).lower():
            print("\n🔑 Falha na autenticação. Verifique o usuário e senha.")
        elif "does not exist" in str(e).lower():
            print("\n❓ Banco de dados não encontrado. Verifique o nome do banco.")
        elif "could not connect to server" in str(e).lower():
            print("\n🔌 Não foi possível conectar ao servidor. Verifique se o PostgreSQL está rodando.")
        
        return False

def main():
    print("🔍 Verificador de Encoding do PostgreSQL")
    print("=" * 50)
    
    # Configurações padrão
    config = {
        'host': 'localhost',
        'port': '5432',
        'dbname': 'postgres',
        'user': input("Usuário (padrão: postgres): ") or "postgres",
        'password': getpass("Senha: ")
    }
    
    print("\n🔄 Conectando ao banco de dados...")
    if test_connection(**config):
        print("\n✅ Verificação concluída com sucesso!")
        
        print("\n📌 Recomendações:")
        print("1. O encoding do banco deve ser 'UTF8'")
        print("2. Para bancos em português, o collate recomendado é 'pt_BR.UTF-8'")
        print("3. Se precisar alterar o encoding, será necessário recriar o banco")
    else:
        print("\n❌ Falha na verificação. Verifique as mensagens de erro acima.")
        
        print("\n🔧 Solução de problemas:")
        print("1. Verifique se o serviço do PostgreSQL está rodando")
        print("2. Confirme se o usuário e senha estão corretos")
        print("3. Tente conectar com o psql para testar as credenciais:")
        print(f"   psql -h localhost -U {config['user']} -d postgres")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
    
    input("\nPressione Enter para sair...")
