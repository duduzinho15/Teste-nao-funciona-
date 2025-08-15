"""
Script para inserir dados de teste na tabela 'partidas'.
"""
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def seed_partidas():
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
            
            # Verifica se já existem partidas
            result = conn.execute(text("SELECT COUNT(*) FROM partidas"))
            count = result.scalar()
            
            if count > 0:
                print(f"ℹ️  Já existem {count} partidas cadastradas no banco.")
                print("   Pulando a inserção de dados de teste.")
                return 0
            
            print("ℹ️  Inserindo dados de teste na tabela 'partidas'...")
            
            # Obtém alguns clubes existentes
            clubes = conn.execute(text("SELECT id, nome FROM clubes LIMIT 10")).fetchall()
            
            if not clubes or len(clubes) < 2:
                print("❌ É necessário ter pelo menos 2 clubes cadastrados para criar partidas de teste.")
                return 1
            
            # Insere partidas de teste
            hoje = datetime.now().date()
            partidas = []
            
            for i in range(0, len(clubes) - 1, 2):
                clube_casa = clubes[i]
                clube_visitante = clubes[i+1] if (i+1) < len(clubes) else clubes[0]
                
                partida = {
                    'data_partida': (hoje - timedelta(days=i)).isoformat(),
                    'hora_partida': '19:00:00',
                    'estadio_id': 1,  # ID do estádio (ajustar conforme necessário)
                    'competicao_id': 1,  # ID da competição (ajustar conforme necessário)
                    'clube_casa_id': clube_casa[0],
                    'clube_visitante_id': clube_visitante[0],
                    'gols_casa': i % 3,
                    'gols_visitante': (i + 1) % 3,
                    'rodada': i + 1,
                    'temporada': '2024',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                partidas.append(partida)
            
            # Insere as partidas
            for p in partidas:
                query = """
                    INSERT INTO partidas (
                        data_partida, hora_partida, estadio_id, competicao_id,
                        clube_casa_id, clube_visitante_id, gols_casa, gols_visitante,
                        rodada, temporada, created_at, updated_at
                    ) VALUES (
                        :data_partida, :hora_partida, :estadio_id, :competicao_id,
                        :clube_casa_id, :clube_visitante_id, :gols_casa, :gols_visitante,
                        :rodada, :temporada, :created_at, :updated_at
                    )
                """
                conn.execute(text(query), p)
            
            conn.commit()
            print(f"✅ {len(partidas)} partidas de teste inseridas com sucesso!")
            
            return 0
            
    except SQLAlchemyError as e:
        print(f"❌ Erro ao inserir dados de teste: {e}")
        return 1
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🌱 Iniciando seed de dados de teste para a tabela 'partidas'...")
    sys.exit(seed_partidas())
