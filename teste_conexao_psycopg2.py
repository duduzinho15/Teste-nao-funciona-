import psycopg2
import sys

def testar_conexao():
    print("🔍 Testando conexão com o PostgreSQL...")
    
    # Tentar diferentes combinações de parâmetros de conexão
    parametros = [
        {
            'host': 'localhost',
            'port': '5432',
            'dbname': 'postgres',
            'user': 'postgres',
            'password': 'postgres',
            'client_encoding': 'UTF8'
        },
        {
            'host': 'localhost',
            'port': '5432',
            'dbname': 'postgres',
            'user': 'postgres',
            'password': 'postgres',
            'options': '-c client_encoding=UTF8'
        },
        {
            'host': 'localhost',
            'port': '5432',
            'dbname': 'postgres',
            'user': 'postgres',
            'password': 'postgres',
            'client_encoding': 'LATIN1'
        }
    ]
    
    for i, params in enumerate(parametros, 1):
        print(f"\n🔧 Tentativa {i}:")
        print(f"   - Host: {params['host']}")
        print(f"   - Porta: {params['port']}")
        print(f"   - Banco: {params['dbname']}")
        print(f"   - Usuário: {params['user']}")
        
        try:
            conn = psycopg2.connect(**params)
            print("✅ Conexão bem-sucedida!")
            
            # Testar consulta simples
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"📊 Versão do PostgreSQL: {version[0]}")
                
                # Verificar encoding do banco
                cur.execute("SHOW server_encoding;")
                encoding = cur.fetchone()[0]
                print(f"🔤 Server Encoding: {encoding}")
                
                cur.execute("SHOW client_encoding;")
                client_encoding = cur.fetchone()[0]
                print(f"🔤 Client Encoding: {client_encoding}")
                
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro na conexão: {str(e)}")
            
    return False

if __name__ == "__main__":
    testar_conexao()
    input("\nPressione Enter para sair...")
