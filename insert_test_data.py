"""
Script para inserir dados de teste nas tabelas de referência e na tabela 'partidas'.
"""
import sys
import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta

def insert_test_data():
    """Insere dados de teste nas tabelas de referência e na tabela 'partidas'."""
    conn = None
    cur = None
    
    try:
        # Parâmetros de conexão
        db_params = {
            'host': 'localhost',
            'database': 'apostapro_db',
            'user': 'apostapro_user',
            'password': 'senha_segura_123',
            'port': '5432'
        }
        
        print("🔍 Conectando ao banco de dados...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = False  # Desativa o autocommit para usar transações
        cur = conn.cursor()
        
        # 1. Inserir dados na tabela 'paises_clubes' se não existirem
        print("\n📝 Inserindo dados de teste na tabela 'paises_clubes'...")
        
        # Verifica se já existem países
        cur.execute("SELECT COUNT(*) FROM paises_clubes;")
        if cur.fetchone()[0] == 0:
            # Insere países de teste
            paises = [
                (1, 'Brasil', 'BRA', 'América do Sul'),
                (2, 'Espanha', 'ESP', 'Europa'),
                (3, 'Inglaterra', 'ENG', 'Europa'),
                (4, 'Itália', 'ITA', 'Europa'),
                (5, 'Alemanha', 'GER', 'Europa')
            ]
            
            for pais in paises:
                cur.execute(
                    """
                    INSERT INTO paises_clubes (id, nome, codigo_iso, continente)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                    """,
                    pais
                )
            
            print(f"✅ Inseridos {len(paises)} países na tabela 'paises_clubes'.")
        else:
            print("ℹ️  A tabela 'paises_clubes' já contém registros. Nenhum dado será inserido.")
        
        # 2. Inserir dados na tabela 'clubes' se não existirem
        print("\n📝 Inserindo dados de teste na tabela 'clubes'...")
        
        # Verifica se já existem clubes
        cur.execute("SELECT COUNT(*) FROM clubes;")
        if cur.fetchone()[0] == 0:
            # Insere clubes de teste
            clubes = [
                (1, 'Flamengo', 'FLA', 1, 'Rio de Janeiro', '1900-01-01', True, 'https://example.com/flamengo.png'),
                (2, 'Barcelona', 'BAR', 2, 'Barcelona', '1899-01-01', True, 'https://example.com/barcelona.png'),
                (3, 'Real Madrid', 'RMA', 2, 'Madrid', '1902-01-01', True, 'https://example.com/realmadrid.png'),
                (4, 'Liverpool', 'LIV', 3, 'Liverpool', '1892-01-01', True, 'https://example.com/liverpool.png'),
                (5, 'Juventus', 'JUV', 4, 'Turim', '1897-01-01', True, 'https://example.com/juventus.png'),
                (6, 'Bayern de Munique', 'BAY', 5, 'Munique', '1900-01-01', True, 'https://example.com/bayern.png')
            ]
            
            for clube in clubes:
                cur.execute(
                    """
                    INSERT INTO clubes (id, nome, abreviacao, pais_id, cidade, fundacao, ativo, url_escudo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                    """,
                    clube
                )
            
            print(f"✅ Inseridos {len(clubes)} clubes na tabela 'clubes'.")
        else:
            print("ℹ️  A tabela 'clubes' já contém registros. Nenhum dado será inserido.")
        
        # 3. Inserir dados na tabela 'competicoes' se não existirem
        print("\n📝 Inserindo dados de teste na tabela 'competicoes'...")
        
        # Verifica se já existem competições
        cur.execute("SELECT COUNT(*) FROM competicoes;")
        if cur.fetchone()[0] == 0:
            # Insere competições de teste
            competicoes = [
                (1, 'Campeonato Brasileiro Série A', 'Brasileirão', 'Liga', 'Brasil', 'A', True, 'https://example.com/brasileirao'),
                (2, 'La Liga', 'LaLiga', 'Liga', 'Espanha', 'A', True, 'https://example.com/laliga'),
                (3, 'Premier League', 'EPL', 'Liga', 'Inglaterra', 'A', True, 'https://example.com/premierleague'),
                (4, 'Copa do Brasil', 'CdB', 'Copa', 'Brasil', 'A', True, 'https://example.com/copadobrasil'),
                (5, 'Champions League', 'UCL', 'Internacional', 'Europa', 'A', True, 'https://example.com/ucl')
            ]
            
            for competicao in competicoes:
                cur.execute(
                    """
                    INSERT INTO competicoes (id, nome, nome_curto, tipo, pais, nivel, ativo, url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                    """,
                    competicao
                )
            
            print(f"✅ Inseridas {len(competicoes)} competições na tabela 'competicoes'.")
        else:
            print("ℹ️  A tabela 'competicoes' já contém registros. Nenhum dado será inserido.")
        
        # 4. Inserir dados na tabela 'estadios' se não existir ou estiver vazia
        print("\n📝 Verificando a tabela 'estadios'...")
        
        # Verifica se a tabela 'estadios' existe
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'estadios'
            );
        """)
        
        if not cur.fetchone()[0]:
            print("❌ A tabela 'estadios' não existe no banco de dados.")
            print("   Criando a tabela 'estadios'...")
            
            # Cria a tabela 'estadios'
            cur.execute("""
                CREATE TABLE IF NOT EXISTS estadios (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    apelido VARCHAR(100),
                    cidade VARCHAR(100),
                    capacidade INTEGER,
                    inauguracao DATE,
                    gramado VARCHAR(50),
                    clube_id INTEGER REFERENCES clubes(id) ON DELETE SET NULL,
                    pais_id INTEGER REFERENCES paises_clubes(id) ON DELETE SET NULL,
                    ativo BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            print("✅ Tabela 'estadios' criada com sucesso.")
        
        # Verifica se a tabela 'estadios' está vazia
        cur.execute("SELECT COUNT(*) FROM estadios;")
        if cur.fetchone()[0] == 0:
            # Insere estádios de teste
            estadios = [
                (1, 'Maracanã', 'Maraca', 'Rio de Janeiro', 78838, '1950-06-16', 'Natural', 1, 1, True),
                (2, 'Camp Nou', 'Camp Nou', 'Barcelona', 99354, '1957-09-24', 'Híbrido', 2, 2, True),
                (3, 'Santiago Bernabéu', 'Bernabéu', 'Madrid', 81044, '1947-12-14', 'Híbrido', 3, 2, True),
                (4, 'Anfield', 'Anfield', 'Liverpool', 53394, '1884-01-01', 'Híbrido', 4, 3, True),
                (5, 'Allianz Arena', 'Allianz', 'Munique', 75024, '2005-05-30', 'Sintético', 6, 5, True)
            ]
            
            for estadio in estadios:
                cur.execute(
                    """
                    INSERT INTO estadios (id, nome, apelido, cidade, capacidade, inauguracao, gramado, clube_id, pais_id, ativo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                    """,
                    estadio
                )
            
            print(f"✅ Inseridos {len(estadios)} estádios na tabela 'estadios'.")
        else:
            print("ℹ️  A tabela 'estadios' já contém registros. Nenhum dado será inserido.")
        
        # 5. Inserir dados na tabela 'partidas' se não existirem
        print("\n📝 Inserindo dados de teste na tabela 'partidas'...")
        
        # Verifica se já existem partidas
        cur.execute("SELECT COUNT(*) FROM partidas;")
        if cur.fetchone()[0] == 0:
            # Obtém os IDs dos clubes e competições
            cur.execute("SELECT id FROM clubes ORDER BY id LIMIT 6;")
            clube_ids = [row[0] for row in cur.fetchall()]
            
            cur.execute("SELECT id FROM competicoes ORDER BY id LIMIT 5;")
            competicao_ids = [row[0] for row in cur.fetchall()]
            
            if len(clube_ids) < 4 or len(competicao_ids) < 2:
                print("❌ Não há clubes ou competições suficientes para criar partidas.")
                conn.rollback()
                return 1
            
            # Data atual para as partidas
            hoje = datetime.now()
            
            # Insere partidas de teste
            partidas = [
                # Partidas passadas
                (1, competicao_ids[0], clube_ids[0], clube_ids[1], hoje - timedelta(days=7), '1ª Rodada', '2024', 2, 1, 'Finalizada', 1, 'https://example.com/partida1', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
                (2, competicao_ids[1], clube_ids[2], clube_ids[3], hoje - timedelta(days=5), 'Jogo 10', '2023/2024', 1, 1, 'Finalizada', 2, 'https://example.com/partida2', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
                # Partidas futuras
                (3, competicao_ids[0], clube_ids[0], clube_ids[4], hoje + timedelta(days=3), '2ª Rodada', '2024', None, None, 'Agendada', 1, 'https://example.com/partida3', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
                (4, competicao_ids[1], clube_ids[5], clube_ids[2], hoje + timedelta(days=5), 'Jogo 11', '2023/2024', None, None, 'Agendada', 3, 'https://example.com/partida4', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
            ]
            
            for partida in partidas:
                try:
                    cur.execute(
                        """
                        INSERT INTO partidas (
                            id, competicao_id, clube_casa_id, clube_visitante_id, data_partida, rodada, 
                            temporada, gols_casa, gols_visitante, status, estadio_id, url_fbref,
                            posse_bola_casa, posse_bola_visitante, finalizacoes_totais_casa, 
                            finalizacoes_totais_visitante, finalizacoes_no_alvo_casa, 
                            finalizacoes_no_alvo_visitante, defesas_casa, defesas_visitante, 
                            escanteios_casa, escanteios_visitante, faltas_casa, faltas_visitante, 
                            impedimentos_casa, impedimentos_visitante, tiro_meta_casa, 
                            tiro_meta_visitante, desefesas_do_goleiro_casa, 
                            defesas_do_goleiro_visitante, cartoes_amarelos_casa, 
                            cartoes_amarelos_visitante, cartoes_vermelhos_casa, 
                            cartoes_vermelhos_visitante
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (id) DO NOTHING;
                        """,
                        partida
                    )
                except psycopg2.Error as e:
                    print(f"❌ Erro ao inserir partida {partida[0]}: {e}")
                    conn.rollback()
                    return 1
            
            print(f"✅ Inseridas {len(partidas)} partidas na tabela 'partidas'.")
        else:
            print("ℹ️  A tabela 'partidas' já contém registros. Nenhum dado será inserido.")
        
        # Confirma as alterações
        conn.commit()
        print("\n✅ Dados de teste inseridos com sucesso!")
        return 0
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        if conn:
            conn.rollback()
        return 1
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        if conn:
            conn.rollback()
        return 1
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("📝 Iniciando a inserção de dados de teste...")
    sys.exit(insert_test_data())
