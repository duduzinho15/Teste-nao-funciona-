-- Script SQL para inserir dados de teste nas tabelas de referência e na tabela 'partidas'

-- 1. Inserir países na tabela 'paises_clubes' se não existirem
INSERT INTO paises_clubes (id, nome, codigo_iso, continente, ativo)
VALUES 
    (1, 'Brasil', 'BRA', 'América do Sul', true),
    (2, 'Espanha', 'ESP', 'Europa', true),
    (3, 'Inglaterra', 'ENG', 'Europa', true),
    (4, 'Itália', 'ITA', 'Europa', true),
    (5, 'Alemanha', 'GER', 'Europa', true)
ON CONFLICT (id) DO NOTHING;

-- 2. Inserir clubes na tabela 'clubes' se não existirem
INSERT INTO clubes (id, nome, abreviacao, pais_id, cidade, fundacao, ativo, url_escudo)
VALUES 
    (1, 'Flamengo', 'FLA', 1, 'Rio de Janeiro', '1895-11-15', true, 'https://example.com/flamengo.png'),
    (2, 'Barcelona', 'BAR', 2, 'Barcelona', '1899-11-29', true, 'https://example.com/barcelona.png'),
    (3, 'Real Madrid', 'RMA', 2, 'Madrid', '1902-03-06', true, 'https://example.com/realmadrid.png'),
    (4, 'Liverpool', 'LIV', 3, 'Liverpool', '1892-06-03', true, 'https://example.com/liverpool.png'),
    (5, 'Juventus', 'JUV', 4, 'Turim', '1897-11-01', true, 'https://example.com/juventus.png'),
    (6, 'Bayern de Munique', 'BAY', 5, 'Munique', '1900-02-27', true, 'https://example.com/bayern.png')
ON CONFLICT (id) DO NOTHING;

-- 3. Inserir competições na tabela 'competicoes' se não existirem
INSERT INTO competicoes (id, nome, nome_curto, tipo, pais, nivel, ativo, url)
VALUES 
    (1, 'Campeonato Brasileiro Série A', 'Brasileirão', 'Liga', 'Brasil', 'A', true, 'https://example.com/brasileirao'),
    (2, 'La Liga', 'LaLiga', 'Liga', 'Espanha', 'A', true, 'https://example.com/laliga'),
    (3, 'Premier League', 'EPL', 'Liga', 'Inglaterra', 'A', true, 'https://example.com/premierleague'),
    (4, 'Copa do Brasil', 'CdB', 'Copa', 'Brasil', 'A', true, 'https://example.com/copadobrasil'),
    (5, 'Champions League', 'UCL', 'Internacional', 'Europa', 'A', true, 'https://example.com/ucl')
ON CONFLICT (id) DO NOTHING;

-- 4. Criar a tabela 'estadios' se não existir
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

-- 5. Inserir estádios na tabela 'estadios' se não existirem
INSERT INTO estadios (id, nome, apelido, cidade, capacidade, inauguracao, gramado, clube_id, pais_id, ativo)
VALUES 
    (1, 'Maracanã', 'Maraca', 'Rio de Janeiro', 78838, '1950-06-16', 'Natural', 1, 1, true),
    (2, 'Camp Nou', 'Camp Nou', 'Barcelona', 99354, '1957-09-24', 'Híbrido', 2, 2, true),
    (3, 'Santiago Bernabéu', 'Bernabéu', 'Madrid', 81044, '1947-12-14', 'Híbrido', 3, 2, true),
    (4, 'Anfield', 'Anfield', 'Liverpool', 53394, '1884-01-01', 'Híbrido', 4, 3, true),
    (5, 'Allianz Arena', 'Allianz', 'Munique', 75024, '2005-05-30', 'Sintético', 6, 5, true)
ON CONFLICT (id) DO NOTHING;

-- 6. Inserir partidas na tabela 'partidas' se não existirem
-- Partidas passadas
INSERT INTO partidas (
    id, competicao_id, clube_casa_id, clube_visitante_id, data_partida, rodada, 
    temporada, gols_casa, gols_visitante, status, estadio_id, url_fbref
)
VALUES 
    (1, 1, 1, 2, CURRENT_DATE - INTERVAL '7 days', '1ª Rodada', '2024', 2, 1, 'Finalizada', 1, 'https://example.com/partida1'),
    (2, 2, 3, 4, CURRENT_DATE - INTERVAL '5 days', 'Jogo 10', '2023/2024', 1, 1, 'Finalizada', 3, 'https://example.com/partida2')
ON CONFLICT (id) DO NOTHING;

-- Partidas futuras
INSERT INTO partidas (
    id, competicao_id, clube_casa_id, clube_visitante_id, data_partida, rodada, 
    temporada, status, estadio_id, url_fbref
)
VALUES 
    (3, 1, 1, 4, CURRENT_DATE + INTERVAL '3 days', '2ª Rodada', '2024', 'Agendada', 1, 'https://example.com/partida3'),
    (4, 2, 5, 3, CURRENT_DATE + INTERVAL '5 days', 'Jogo 11', '2023/2024', 'Agendada', 5, 'https://example.com/partida4')
ON CONFLICT (id) DO NOTHING;

-- 7. Inserir estatísticas para as partidas finalizadas
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

-- 8. Verificar os dados inseridos
SELECT 'paises_clubes' AS tabela, COUNT(*) AS registros FROM paises_clubes
UNION ALL
SELECT 'clubes' AS tabela, COUNT(*) AS registros FROM clubes
UNION ALL
SELECT 'competicoes' AS tabela, COUNT(*) AS registros FROM competicoes
UNION ALL
SELECT 'estadios' AS tabela, COUNT(*) AS registros FROM estadios
UNION ALL
SELECT 'partidas' AS tabela, COUNT(*) AS registros FROM partidas
UNION ALL
SELECT 'estatisticas_partidas' AS tabela, COUNT(*) AS registros FROM estatisticas_partidas;
