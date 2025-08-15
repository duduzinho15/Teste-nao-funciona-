"""
Script simples para verificar o conteúdo da tabela partidas.
"""
import psycopg2

def check_partidas():
    # Configurações do banco de dados
    db_config = {
        'host': 'localhost',
        'database': 'apostapro_db',
        'user': 'apostapro_user',
        'password': 'senha_segura_123',
        'port': '5432'
    }
    
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        print("🔍 Verificando a tabela 'partidas'...")
        
        # Verifica se a tabela existe
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'partidas'
            );
        """)
        
        if not cur.fetchone()[0]:
            print("❌ A tabela 'partidas' não existe no banco de dados.")
            return
        
        # Conta o número de registros
        cur.execute("SELECT COUNT(*) FROM partidas;")
        count = cur.fetchone()[0]
        print(f"📊 Total de partidas: {count}")
        
        if count > 0:
            # Mostra as colunas da tabela
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'partidas';
            """)
            
            print("\n📋 Estrutura da tabela 'partidas':")
            for col in cur.fetchall():
                print(f"- {col[0]}: {col[1]}")
            
            # Mostra algumas partidas de exemplo
            cur.execute("""
                SELECT p.id, p.data_partida, 
                       c1.nome AS clube_casa, c2.nome AS clube_visitante,
                       p.gols_casa, p.gols_visitante, p.status
                FROM partidas p
                JOIN clubes c1 ON p.clube_casa_id = c1.id
                JOIN clubes c2 ON p.clube_visitante_id = c2.id
                ORDER BY p.data_partida
                LIMIT 5;
            """)
            
            print("\n📋 Partidas encontradas:")
            for row in cur.fetchall():
                print(f"- ID: {row[0]}, Data: {row[1]}, {row[2]} {row[4] or '?'} x {row[5] or '?'} {row[3]}, Status: {row[6]}")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
    except psycopg2.Error as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_partidas()
