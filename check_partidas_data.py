"""
Script para verificar os dados na tabela partidas.
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
        
        print("🔍 Verificando dados na tabela 'partidas'...")
        
        # Conta o número de partidas
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
            
            # Mostra as partidas
            cur.execute("""
                SELECT p.id, p.data_partida, 
                       c1.nome AS clube_casa, c2.nome AS clube_visitante,
                       p.gols_casa, p.gols_visitante, p.status, p.rodada
                FROM partidas p
                JOIN clubes c1 ON p.clube_casa_id = c1.id
                JOIN clubes c2 ON p.clube_visitante_id = c2.id
                ORDER BY p.data_partida;
            """)
            
            print("\n📋 Partidas encontradas:")
            for row in cur.fetchall():
                id_partida, data, casa, visitante, gols_casa, gols_visitante, status, rodada = row
                print(f"- ID: {id_partida}, Data: {data}, Rodada: {rodada}")
                print(f"  {casa} {gols_casa or '?'} x {gols_visitante or '?'} {visitante}")
                print(f"  Status: {status}")
        else:
            print("❌ Nenhuma partida encontrada na tabela.")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False
    except psycopg2.Error as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_partidas()
