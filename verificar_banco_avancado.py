import psycopg2
from psycopg2 import sql
import psycopg2.extras

def testar_conexao_avancada():
    """Testa a conexão com o banco de dados usando diferentes configurações"""
    print("🔍 Testando conexão avançada com o banco de dados...")
    
    # Lista de configurações para testar
    configs = [
        {
            'name': 'Conexão direta com tratamento de erros',
            'dbname': 'apostapro_db_utf8',
            'user': 'postgres',
            'password': '123456789',
            'host': 'localhost',
            'port': 5432,
            'client_encoding': 'UTF8',
            'options': '-c client_encoding=UTF8',
            'connect_timeout': 5
        },
        {
            'name': 'Conexão com encoding LATIN1',
            'dbname': 'apostapro_db_utf8',
            'user': 'postgres',
            'password': '123456789',
            'host': 'localhost',
            'port': 5432,
            'client_encoding': 'LATIN1',
            'connect_timeout': 5
        },
        {
            'name': 'Conexão sem especificar encoding',
            'dbname': 'apostapro_db_utf8',
            'user': 'postgres',
            'password': '123456789',
            'host': 'localhost',
            'port': 5432,
            'connect_timeout': 5
        }
    ]
    
    for config in configs:
        print(f"\n🔧 Testando configuração: {config['name']}")
        
        try:
            # Remover a chave 'name' antes de conectar
            conn_params = {k: v for k, v in config.items() if k != 'name'}
            
            # Tentar conexão com tratamento de erros
            with psycopg2.connect(**conn_params) as conn:
                print(f"✅ Conexão bem-sucedida!")
                
                # Usar um cursor com tratamento de erros
                with conn.cursor() as cur:
                    # Tentar listar as tabelas
                    try:
                        cur.execute("""
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public';
                        """)
                        
                        tabelas = cur.fetchall()
                        print(f"\n📋 Tabelas encontradas ({len(tabelas)}):")
                        
                        for tabela in tabelas:
                            tabela = tabela[0]  # Extrair o nome da tabela da tupla
                            print(f"\n🔍 Tabela: {tabela}")
                            
                            # Tentar contar registros
                            try:
                                cur.execute(sql.SQL('SELECT COUNT(*) FROM {}').format(sql.Identifier(tabela)))
                                count = cur.fetchone()[0]
                                print(f"   📊 Total de registros: {count}")
                                
                                # Se a contagem for pequena, mostrar algumas linhas
                                if count > 0 and count <= 5:
                                    try:
                                        cur.execute(sql.SQL('SELECT * FROM {} LIMIT 3').format(sql.Identifier(tabela)))
                                        colnames = [desc[0] for desc in cur.description]
                                        print(f"   📝 Colunas: {', '.join(colnames)}")
                                        print("   📄 Primeiras linhas:")
                                        for row in cur.fetchall():
                                            print(f"      {row}")
                                    except Exception as e:
                                        print(f"   ⚠️  Erro ao ler dados: {e}")
                                        
                            except Exception as e:
                                print(f"   ⚠️  Erro ao contar registros: {e}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao listar tabelas: {e}")
                        
        except Exception as e:
            print(f"❌ Falha na conexão: {e}")
            
            # Se for erro de codificação, tentar com tratamento de erros
            if 'codec' in str(e) or 'encoding' in str(e).lower():
                print("   🔄 Tentando com tratamento de erros de codificação...")
                try:
                    conn_params['client_encoding'] = 'LATIN1'
                    with psycopg2.connect(**conn_params) as conn:
                        with conn.cursor() as cur:
                            cur.execute("SHOW server_encoding;")
                            print(f"   ✅ Conexão bem-sucedida com encoding LATIN1!")
                            print(f"   🔄 Encoding do servidor: {cur.fetchone()[0]}")
                except Exception as e2:
                    print(f"   ❌ Falha mesmo com tratamento de erros: {e2}")

if __name__ == "__main__":
    print("\n🔄 Verificação Avançada do Banco de Dados")
    print("=" * 50)
    testar_conexao_avancada()
    input("\nPressione Enter para sair...")
