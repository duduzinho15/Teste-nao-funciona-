"""
Script para testar a inserção de um registro na tabela 'partidas'.
"""
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

def test_insert():
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
            
            # Obtém os primeiros 2 clubes para usar no teste
            clubes = conn.execute(text("SELECT id FROM clubes LIMIT 2")).fetchall()
            
            if len(clubes) < 2:
                print("❌ É necessário ter pelo menos 2 clubes cadastrados para criar uma partida de teste.")
                return 1
            
            # Dados de teste
            partida = {
                'data_partida': '2024-01-01',
                'hora_partida': '19:00:00',
                'estadio_id': 1,  # Supondo que exista um estádio com ID 1
                'competicao_id': 1,  # Supondo que exista uma competição com ID 1
                'clube_casa_id': clubes[0][0],
                'clube_visitante_id': clubes[1][0],
                'gols_casa': 2,
                'gols_visitante': 1,
                'rodada': 1,
                'temporada': '2024',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            print("\nℹ️  Tentando inserir partida de teste:", partida)
            
            # Tenta inserir
            try:
                conn.execute(text("""
                    INSERT INTO partidas (
                        data_partida, hora_partida, estadio_id, competicao_id,
                        clube_casa_id, clube_visitante_id, gols_casa, gols_visitante,
                        rodada, temporada, created_at, updated_at
                    ) VALUES (
                        :data_partida, :hora_partida, :estadio_id, :competicao_id,
                        :clube_casa_id, :clube_visitante_id, :gols_casa, :gols_visitante,
                        :rodada, :temporada, :created_at, :updated_at
                    )
                """), partida)
                
                conn.commit()
                print("✅ Partida de teste inserida com sucesso!")
                
                # Verifica se a partida foi inserida
                result = conn.execute(text("SELECT id FROM partidas ORDER BY id DESC LIMIT 1"))
                partida_id = result.scalar()
                print(f"📌 ID da partida inserida: {partida_id}")
                
                return 0
                
            except IntegrityError as e:
                print(f"❌ Erro de integridade ao inserir partida: {e.orig}")
                print("   Verifique se as chaves estrangeiras (estadio_id, competicao_id, clube_casa_id, clube_visitante_id) existem.")
                return 1
                
    except SQLAlchemyError as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
        return 1
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🔍 Iniciando teste de inserção na tabela 'partidas'...")
    sys.exit(test_insert())
