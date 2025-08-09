import psycopg2

def main():
    print("🔍 Verificando banco de dados...")
    
    try:
        # Configurações de conexão
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="apostapro_db",
            user="apostapro_user",
            password="senha_segura_123"
        )
        
        print("✅ Conectado ao banco de dados com sucesso!")
        
        # Verifica se a tabela posts_redes_sociais existe
        with conn.cursor() as cur:
            # Lista todas as tabelas
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = [row[0] for row in cur.fetchall()]
            print("\n📋 Tabelas encontradas:")
            for table in tables:
                print(f"- {table}")
            
            # Verifica se a tabela posts_redes_sociais existe
            if 'posts_redes_sociais' in tables:
                print("\n✅ A tabela 'posts_redes_sociais' existe!")
                
                # Mostra as colunas da tabela
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'posts_redes_sociais';
                """)
                
                print("\n📋 Colunas da tabela 'posts_redes_sociais':")
                for col_name, data_type in cur.fetchall():
                    print(f"- {col_name} ({data_type})")
            else:
                print("\n❌ A tabela 'posts_redes_sociais' NÃO foi encontrada.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    main()
