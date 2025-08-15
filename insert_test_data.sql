-- Script para inserir dados de teste para o endpoint /matches

-- Inserir países
INSERT INTO paises_clubes (id, nome, codigo_iso, continente)
VALUES 
(1, 'Brasil', 'BRA', 'América do Sul'),
(2, 'Espanha', 'ESP', 'Europa'),
(3, 'Inglaterra', 'ENG', 'Europa'),
(4, 'Itália', 'ITA', 'Europa'),
(5, 'Alemanha', 'GER', 'Europa')
ON CONFLICT (id) DO NOTHING;

-- Inserir competições
INSERT INTO competicoes (id, nome, nome_curto, tipo, pais, nivel, ativo, url)
VALUES 
(1, 'Campeonato Brasileiro Série A', 'Brasileirão', 'Liga', 'Brasil', 'A', TRUE, 'https://example.com/brasileirao'),
(2, 'La Liga', 'LaLiga', 'Liga', 'Espanha', 'A', TRUE, 'https://example.com/laliga'),
(3, 'Premier League', 'EPL', 'Liga', 'Inglaterra', 'A', TRUE, 'https://example.com/premierleague'),
(4, 'Copa do Brasil', 'CdB', 'Copa', 'Brasil', 'A', TRUE, 'https://example.com/copadobrasil'),
(5, 'Champions League', 'UCL', 'Internacional', 'Europa', 'A', TRUE, 'https://example.com/ucl')
ON CONFLICT (id) DO NOTHING;

-- Inserir clubes
INSERT INTO clubes (id, nome, abreviacao, pais_id, cidade, fundacao, ativo, url_escudo)
VALUES 
(1, 'Flamengo', 'FLA', 1, 'Rio de Janeiro', '1895-11-15', TRUE, 'https://example.com/flamengo.png'),
(2, 'Barcelona', 'BAR', 2, 'Barcelona', '1899-11-29', TRUE, 'https://example.com/barcelona.png'),
(3, 'Real Madrid', 'RMA', 2, 'Madrid', '1902-03-06', TRUE, 'https://example.com/realmadrid.png'),
(4, 'Liverpool', 'LIV', 3, 'Liverpool', '1892-06-03', TRUE, 'https://example.com/liverpool.png'),
(5, 'Juventus', 'JUV', 4, 'Turim', '1897-11-01', TRUE, 'https://example.com/juventus.png'),
(6, 'Bayern de Munique', 'BAY', 5, 'Munique', '1900-02-27', TRUE, 'https://example.com/bayern.png')
ON CONFLICT (id) DO NOTHING;

-- Criar tabela estadios se não existir
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

-- Inserir estádios
INSERT INTO estadios (id, nome, apelido, cidade, capacidade, inauguracao, gramado, clube_id, pais_id, ativo)
VALUES 
(1, 'Maracanã', 'Maraca', 'Rio de Janeiro', 78838, '1950-06-16', 'Natural', 1, 1, TRUE),
(2, 'Camp Nou', 'Camp Nou', 'Barcelona', 99354, '1957-09-24', 'Híbrido', 2, 2, TRUE),
(3, 'Santiago Bernabéu', 'Bernabéu', 'Madrid', 81044, '1947-12-14', 'Híbrido', 3, 2, TRUE),
(4, 'Anfield', 'Anfield', 'Liverpool', 53394, '1884-01-01', 'Híbrido', 4, 3, TRUE),
(5, 'Allianz Arena', 'Allianz', 'Munique', 75024, '2005-05-30', 'Sintético', 6, 5, TRUE)
ON CONFLICT (id) DO NOTHING;

-- Inserir partidas
INSERT INTO partidas (
    id, competicao_id, clube_casa_id, clube_visitante_id, data_partida, 
    rodada, temporada, gols_casa, gols_visitante, status, estadio_id, url_fbref
)
VALUES 
(1, 1, 1, 2, '2024-05-15 19:00:00', '1ª Rodada', '2024', 2, 1, 'Finalizada', 1, 'https://example.com/partida1'),
(2, 2, 3, 4, '2024-05-16 20:00:00', 'Jogo 10', '2023/2024', 1, 1, 'Finalizada', 3, 'https://example.com/partida2'),
(3, 1, 1, 4, '2024-05-20 16:00:00', '2ª Rodada', '2024', NULL, NULL, 'Agendada', 1, 'https://example.com/partida3'),
(4, 2, 5, 3, '2024-05-22 21:00:00', 'Jogo 11', '2023/2024', NULL, NULL, 'Agendada', 5, 'https://example.com/partida4')
ON CONFLICT (id) DO NOTHING;

-- Inserir estatísticas das partidas
INSERT INTO estatisticas_partidas (
    partida_id, posse_bola_casa, posse_bola_visitante, finalizacoes_totais_casa, 
    finalizacoes_totais_visitante, finalizacoes_no_alvo_casa, finalizacoes_no_alvo_visitante,
    defesas_casa, defesas_visitante, escanteios_casa, escanteios_visitante,
    faltas_casa, faltas_visitante, impedimentos_casa, impedimentos_visitante,
    tiro_meta_casa, tiro_meta_visitante, defesas_do_goleiro_casa,
    defesas_do_goleiro_visitante, cartoes_amarelos_casa, cartoes_amarelos_visitante,
    cartoes_vermelhos_casa, cartoes_vermelhos_visitante
)
VALUES 
(1, 55, 45, 15, 10, 7, 4, 3, 5, 6, 4, 12, 14, 2, 1, 4, 5, 4, 3, 2, 1, 0, 0),
(2, 48, 52, 12, 14, 5, 6, 5, 4, 5, 7, 10, 12, 1, 3, 6, 4, 6, 5, 3, 4, 0, 1)
ON CONFLICT (partida_id) DO NOTHING;

-- Verificar os dados inseridos
SELECT 'Países inseridos:' AS mensagem, COUNT(*) AS total FROM paises_clubes
UNION ALL
SELECT 'Competições inseridas:', COUNT(*) FROM competicoes
UNION ALL
SELECT 'Clubes inseridos:', COUNT(*) FROM clubes
UNION ALL
SELECT 'Estádios inseridos:', COUNT(*) FROM estadios
UNION ALL
SELECT 'Partidas inseridas:', COUNT(*) FROM partidas
UNION ALL
SELECT 'Estatísticas de partidas inseridas:', COUNT(*) FROM estatisticas_partidas;
