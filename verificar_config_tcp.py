import psycopg2

def check_postgresql_conf():
    print("🔍 Verificando configurações do PostgreSQL...")
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            dbname='postgres',
            user='apostapro_user',
            password='Canjica@@2025'
        )
        
        with conn.cursor() as cur:
            # Verificar configurações de conexão
            cur.execute("SHOW listen_addresses;")
            listen_addresses = cur.fetchone()[0]
            print(f"📡 Listen addresses: {listen_addresses}")
            
            cur.execute("SHOW port;")
            port = cur.fetchone()[0]
            print(f"🔌 Porta PostgreSQL: {port}")
            
            cur.execute("SHOW unix_socket_directories;")
            socket_dirs = cur.fetchone()[0]
            print(f"📁 Diretórios de socket: {socket_dirs}")
            
            print("\n🔍 Verificando configurações adicionais...")
            
            # Verificar configurações de autenticação
            cur.execute("""
                SELECT type, database, user_name, auth_method 
                FROM pg_hba_file_rules 
                WHERE type = 'host' OR type = 'local';
            """)
            
            print("\n🔐 Regras de autenticação (pg_hba.conf):")
            for row in cur.fetchall():
                print(f" - Tipo: {row[0]}, Banco: {row[1]}, Usuário: {row[2]}, Método: {row[3]}")
            
            # Verificar conexões ativas
            cur.execute("""
                SELECT pid, application_name, state, client_addr, client_port
                FROM pg_stat_activity 
                WHERE pid <> pg_backend_pid();
            """)
            
            print("\n🌐 Conexões ativas:")
            connections = cur.fetchall()
            if connections:
                for conn_info in connections:
                    print(f" - PID: {conn_info[0]}, App: {conn_info[1]}, Estado: {conn_info[2]}, Endereço: {conn_info[3]}, Porta: {conn_info[4]}")
            else:
                print(" - Nenhuma outra conexão ativa no momento.")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar configurações: {e}")
        print("\n📌 Verifique se o PostgreSQL está rodando e as credenciais estão corretas.")
        return False

if __name__ == "__main__":
    check_postgresql_conf()
    print("\n✅ Verificação concluída. Verifique as configurações acima.")
