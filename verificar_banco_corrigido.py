import psycopg2

def testar_conexao():
    """Testa a conexão com o banco de dados corrigido"""
    print("🔍 Testando conexão com o banco de dados corrigido...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="apostapro_db_utf8",
            user="postgres",
            password="123456789"
        )
        
        print("✅ Conexão bem-sucedida com o banco de dados corrigido!")
        
        with conn.cursor() as cur:
            # Verificar tabelas no banco de dados
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tabelas = [row[0] for row in cur.fetchall()]
            
            if tabelas:
                print(f"\n📋 Tabelas encontradas ({len(tabelas)}):")
                for tabela in tabelas:
                    print(f" - {tabela}")
                    
                    # Contar registros em cada tabela
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM \"{tabela}\"")
                        count = cur.fetchone()[0]
                        print(f"   📊 Total de registros: {count}")
                    except Exception as e:
                        print(f"   ⚠️  Erro ao contar registros: {e}")
            else:
                print("\nℹ️  Nenhuma tabela encontrada no banco de dados.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False

if __name__ == "__main__":
    print("\n🔄 Verificando banco de dados corrigido...")
    testar_conexao()
    input("\nPressione Enter para sair...")
