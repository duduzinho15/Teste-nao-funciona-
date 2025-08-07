import psycopg2
from getpass import getpass

def check_postgresql_conf_admin():
    print("🔍 Verificando configurações do PostgreSQL (como admin)...")
    
    # Solicitar credenciais de administrador
    print("\n🔑 Por favor, insira as credenciais de administrador do PostgreSQL")
    admin_user = input("Usuário admin (padrão: postgres): ") or "postgres"
    admin_password = getpass("Senha: ")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            dbname='postgres',
            user=admin_user,
            password=admin_password
        )
        
        with conn.cursor() as cur:
            # Verificar configurações de conexão
            cur.execute("SHOW listen_addresses;")
            listen_addresses = cur.fetchone()[0]
            print(f"\n📡 Listen addresses: {listen_addresses}")
            
            cur.execute("SHOW port;")
            port = cur.fetchone()[0]
            print(f"🔌 Porta PostgreSQL: {port}")
            
            # Tentar obter diretórios de socket (requer privilégios)
            try:
                cur.execute("SHOW unix_socket_directories;")
                socket_dirs = cur.fetchone()[0]
                print(f"📁 Diretórios de socket: {socket_dirs}")
            except Exception as e:
                print(f"⚠️  Não foi possível verificar diretórios de socket: {e}")
            
            # Verificar configurações de autenticação
            print("\n🔐 Regras de autenticação (pg_hba.conf):")
            try:
                cur.execute("""
                    SELECT type, database, user_name, auth_method, address
                    FROM pg_hba_file_rules 
                    ORDER BY line_number;
                """)
                
                for row in cur.fetchall():
                    db = 'all' if row[1] is None else ', '.join(row[1])
                    user = 'all' if row[2] is None else ', '.join(row[2])
                    addr = row[4] if row[4] is not None else 'local'
                    print(f" - Tipo: {row[0]}, Banco: {db}, Usuário: {user}, Método: {row[3]}, Endereço: {addr}")
            except Exception as e:
                print(f"⚠️  Não foi possível verificar pg_hba.conf: {e}")
            
            # Verificar encoding do banco de dados
            print("\n🔤 Encoding do banco de dados:")
            cur.execute("SELECT datname, pg_encoding_to_char(encoding) FROM pg_database WHERE datname = 'apostapro_db';")
            db_encoding = cur.fetchone()
            if db_encoding:
                print(f" - {db_encoding[0]}: {db_encoding[1]}")
            else:
                print("⚠️  Banco de dados 'apostapro_db' não encontrado")
            
            # Verificar conexões ativas
            print("\n🌐 Conexões ativas:")
            try:
                cur.execute("""
                    SELECT pid, application_name, state, client_addr, client_port, backend_start
                    FROM pg_stat_activity 
                    WHERE pid <> pg_backend_pid();
                """)
                
                connections = cur.fetchall()
                if connections:
                    for conn_info in connections:
                        print(f" - PID: {conn_info[0]}, App: {conn_info[1]}, Estado: {conn_info[2]}, Endereço: {conn_info[3]}, Porta: {conn_info[4]}, Início: {conn_info[5]}")
                else:
                    print(" - Nenhuma outra conexão ativa no momento.")
            except Exception as e:
                print(f"⚠️  Não foi possível verificar conexões ativas: {e}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar ao PostgreSQL: {e}")
        print("\n📌 Verifique se:")
        print("1. O serviço do PostgreSQL está rodando")
        print("2. As credenciais de administrador estão corretas")
        print("3. O usuário tem permissões suficientes")
        return False

if __name__ == "__main__":
    check_postgresql_conf_admin()
    print("\n✅ Verificação concluída.")
