#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para testar a conexão com o banco de dados PostgreSQL
"""
import psycopg2
import sys
import traceback

def testar_conexao():
    """Testa a conexão com o banco de dados"""
    # Configuração de conexão
    config = {
        "host": "localhost",
        "database": "postgres",
        "user": "postgres",
        "password": "@Eduardo123",
        "port": "5432"
    }
    
    print(f"\n=== Teste de Conexão PostgreSQL ===")
    print(f"Host: {config['host']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print(f"Port: {config['port']}")
    print("=" * 30)
    
    try:
        # Tenta conectar com encoding explícito
        print("\nTentando conectar ao banco de dados...")
        conn = psycopg2.connect(
            host=config["host"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
            port=config["port"],
            client_encoding='UTF8',
            connect_timeout=5
        )
        
        # Se chegou aqui, a conexão foi bem-sucedida
        print("✅ Conexão bem-sucedida!")
        
        # Obtém informações do servidor
        with conn.cursor() as cur:
            # Versão do PostgreSQL
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"\n📋 Versão do PostgreSQL: {version}")
            
            # Codificação do banco de dados
            cur.execute("SELECT current_database(), pg_encoding_to_char(encoding) "
                       "FROM pg_database WHERE datname = current_database();")
            db_info = cur.fetchone()
            print(f"\n💾 Banco de dados: {db_info[0]}")
            print(f"🔤 Codificação: {db_info[1]}")
            
            # Collation e CTYPE
            cur.execute("SELECT datcollate, datctype FROM pg_database WHERE datname = current_database();")
            collation_info = cur.fetchone()
            print(f"🔡 Collation: {collation_info[0]}")
            print(f"🔠 CTYPE: {collation_info[1]}")
            
            # Lista de bancos de dados disponíveis
            print("\n📂 Bancos de dados disponíveis:")
            cur.execute("SELECT datname, pg_encoding_to_char(encoding) "
                       "FROM pg_database WHERE datistemplate = false;")
            for db in cur.fetchall():
                print(f"- {db[0]} (encoding: {db[1]})")
            
            # Verifica se o banco 'apostapro' existe
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'apostapro'")
            if cur.fetchone():
                print("\nℹ️  O banco de dados 'apostapro' existe.")
                
                # Tenta conectar ao banco apostapro
                conn.close()
                config["database"] = "apostapro"
                print(f"\nTentando conectar ao banco 'apostapro'...")
                
                try:
                    conn = psycopg2.connect(
                        host=config["host"],
                        database=config["database"],
                        user=config["user"],
                        password=config["password"],
                        port=config["port"],
                        client_encoding='UTF8',
                        connect_timeout=5
                    )
                    print("✅ Conexão com 'apostapro' bem-sucedida!")
                    
                    # Verifica tabelas no banco apostapro
                    with conn.cursor() as cur_aposta:
                        cur_aposta.execute("""
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public'
                            ORDER BY table_name;
                        """)
                        tabelas = [row[0] for row in cur_aposta.fetchall()]
                        
                        if tabelas:
                            print("\n📊 Tabelas no banco 'apostapro':")
                            for tabela in tabelas:
                                print(f"- {tabela}")
                        else:
                            print("\nℹ️  Nenhuma tabela encontrada no banco 'apostapro'.")
                            
                except Exception as e:
                    print(f"\n❌ Erro ao conectar ao banco 'apostapro': {e}")
                    print("Dica: Verifique se o usuário tem permissão para acessar este banco.")
            else:
                print("\nℹ️  O banco de dados 'apostapro' não foi encontrado.")
        
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Erro de conexão: {e}")
        print("\nVerifique se:")
        print("1. O servidor PostgreSQL está em execução")
        print("2. O nome de usuário e senha estão corretos")
        print("3. O usuário tem permissão para acessar o banco de dados")
        print("4. O firewall não está bloqueando a conexão (porta 5432)")
        return False
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("\nDetalhes do erro:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Configura o encoding da saída do console para UTF-8 no Windows
    if sys.platform == 'win32':
        import io
        import sys
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    testar_conexao()
    
    print("\nPressione Enter para sair...")
    input()
