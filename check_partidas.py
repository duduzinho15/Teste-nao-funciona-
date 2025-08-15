"""
Script para verificar o conteúdo da tabela 'partidas'.
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def check_partidas():
    # String de conexão
    conn_str = "postgresql://apostapro_user:senha_segura_123@localhost:5432/apostapro_db"
    
    try:
        print("🔍 Conectando ao banco de dados...")
        engine = create_engine(conn_str)
        
        with engine.connect() as conn:
            # Verifica se a tabela existe
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'partidas')"
            ))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ A tabela 'partidas' não existe no banco de dados.")
                return 1
            
            print("✅ Tabela 'partidas' encontrada.")
            
            # Conta o número de partidas
            result = conn.execute(text("SELECT COUNT(*) FROM partidas"))
            count = result.scalar()
            print(f"📊 Total de partidas no banco: {count}")
            
            if count > 0:
                # Mostra as primeiras 5 partidas
                print("\n📋 Primeiras 5 partidas:")
                result = conn.execute(text("""
                    SELECT 
                        id, 
                        data_partida, 
                        (SELECT nome FROM clubes WHERE id = clube_casa_id) AS clube_casa,
                        (SELECT nome FROM clubes WHERE id = clube_visitante_id) AS clube_visitante,
                        gols_casa,
                        gols_visitante
                    FROM partidas 
                    ORDER BY data_partida DESC 
                    LIMIT 5
                """))
                
                for row in result:
                    print(f"\n🏆 Partida ID: {row.id}")
                    print(f"📅 Data: {row.data_partida}" if row.data_partida else "📅 Data: Não informada")
                    print(f"🏠 Casa: {row.clube_casa or 'Desconhecido'} {row.gols_casa if row.gols_casa is not None else '-'}")
                    print(f"🛫 Visitante: {row.clube_visitante or 'Desconhecido'} {row.gols_visitante if row.gols_visitante is not None else '-'}")
            
            return 0
            
    except Exception as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
        return 1
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🔍 Verificando a tabela 'partidas' no banco de dados...")
    sys.exit(check_partidas())
