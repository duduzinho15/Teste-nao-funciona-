import psycopg2
from psycopg2 import OperationalError
import sys

def testar_conexao_com_encoding():
    """Testa diferentes configurações de encoding para a conexão com o PostgreSQL"""
    configs = [
        {
            'name': 'UTF-8 padrão',
            'conn_params': {
                'host': 'localhost',
                'port': 5432,
                'dbname': 'apostapro_db',
                'user': 'postgres',
                'password': 'postgres',
                'client_encoding': 'UTF8'
            }
        },
        {
            'name': 'LATIN1',
            'conn_params': {
                'host': 'localhost',
                'port': 5432,
                'dbname': 'apostapro_db',
                'user': 'postgres',
                'password': 'postgres',
                'client_encoding': 'LATIN1'
            }
        },
        {
            'name': 'WIN1252',
            'conn_params': {
                'host': 'localhost',
                'port': 5432,
                'dbname': 'apostapro_db',
                'user': 'postgres',
                'password': 'postgres',
                'client_encoding': 'WIN1252'
            }
        },
        {
            'name': 'Sem encoding específico',
            'conn_params': {
                'host': 'localhost',
                'port': 5432,
                'dbname': 'apostapro_db',
                'user': 'postgres',
                'password': 'postgres'
            }
        }
    ]

    for config in configs:
        print(f"\n🔧 Testando configuração: {config['name']}")
        print(f"📌 Parâmetros: {config['conn_params']}")
        
        try:
            # Tentar conexão com os parâmetros atuais
            conn = psycopg2.connect(**config['conn_params'])
            
            # Se chegou aqui, a conexão foi bem-sucedida
            print("✅ Conexão bem-sucedida!")
            
            # Obter informações do servidor
            with conn.cursor() as cur:
                # Versão do PostgreSQL
                cur.execute("SELECT version();")
                print(f"📊 {cur.fetchone()[0]}")
                
                # Encoding atual
                cur.execute("SHOW server_encoding;")
                print(f"🔤 Server Encoding: {cur.fetchone()[0]}")
                
                cur.execute("SHOW client_encoding;")
                print(f"🔤 Client Encoding: {cur.fetchone()[0]}")
                
                # Verificar se há dados na tabela
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
                tabelas = [row[0] for row in cur.fetchall()]
                
                if tabelas:
                    print(f"\n📋 Tabelas encontradas ({len(tabelas)}):")
                    for tabela in tabelas[:10]:  # Mostrar no máximo 10 tabelas
                        print(f" - {tabela}")
                    if len(tabelas) > 10:
                        print(f" - ... e mais {len(tabelas) - 10} tabelas")
                else:
                    print("\nℹ️  Nenhuma tabela encontrada no banco de dados.")
            
            conn.close()
            return True
            
        except OperationalError as e:
            print(f"❌ Erro de conexão: {e}")
        except UnicodeDecodeError as e:
            print(f"❌ Erro de decodificação: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
    
    print("\n❌ Nenhuma das configurações de encoding funcionou.")
    return False

if __name__ == "__main__":
    print("🔍 Testando diferentes configurações de encoding para conexão com o PostgreSQL")
    print("=" * 80)
    testar_conexao_com_encoding()
    input("\nPressione Enter para sair...")
