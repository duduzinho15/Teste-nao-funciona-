-- Script SQL para inserir dados mínimos no banco de dados
-- Garante que todas as restrições de chave estrangeira sejam respeitadas

-- 1. Limpar tabelas (em ordem reversa para evitar problemas de chave estrangeira)
TRUNCATE TABLE estatisticas_partidas CASCADE;
TRUNCATE TABLE partidas CASCADE;
TRUNCATE TABLE estadios CASCADE;
TRUNCATE TABLE clubes CASCADE;
TRUNCATE TABLE competicoes CASCADE;
TRUNCATE TABLE paises_clubes CASCADE;

-- 2. Inserir países
INSERT INTO paises_clubes (id, nome, codigo_iso, continente)
VALUES 
  (1, 'Brasil', 'BRA', 'América do Sul'),
  (2, 'Espanha', 'ESP', 'Europa'),
  (3, 'Inglaterra', 'ENG', 'Europa'),
  (4, 'Itália', 'ITA', 'Europa'),
  (5, 'Alemanha', 'GER', 'Europa')
ON CONFLICT (id) DO NOTHING;

-- 3. Inserir competições
INSERT INTO competicoes (id, nome, nome_curto, tipo, pais, nivel)
VALUES 
  (1, 'Campeonato Brasileiro Série A', 'Brasileirão', 'Liga', 'Brasil', 'A'),
  (2, 'La Liga', 'LaLiga', 'Liga', 'Espanha', 'A'),
  (3, 'Premier League', 'Premier', 'Liga', 'Inglaterra', 'A')
ON CONFLICT (id) DO NOTHING;

-- 4. Inserir clubes
INSERT INTO clubes (id, nome, abreviacao, pais_id, cidade, fundacao)
VALUES 
  (1, 'Flamengo', 'FLA', 1, 'Rio de Janeiro', '1895-11-15'),
  (2, 'Barcelona', 'BAR', 2, 'Barcelona', '1899-11-29'),
  (3, 'Real Madrid', 'RMA', 2, 'Madrid', '1902-03-06'),
  (4, 'Liverpool', 'LIV', 3, 'Liverpool', '1892-06-03'),
  (5, 'Juventus', 'JUV', 4, 'Turim', '1897-11-01'),
  (6, 'Bayern de Munique', 'BAY', 5, 'Munique', '1900-02-27')
ON CONFLICT (id) DO NOTHING;

-- 5. Inserir estádios
INSERT INTO estadios (id, nome, apelido, cidade, capacidade, inauguracao, clube_id, pais_id)
VALUES 
  (1, 'Maracanã', 'Maraca', 'Rio de Janeiro', 78838, '1950-06-16', 1, 1),
  (2, 'Camp Nou', 'Camp Nou', 'Barcelona', 99354, '1957-09-24', 2, 2),
  (3, 'Santiago Bernabéu', 'Bernabéu', 'Madrid', 81044, '1947-12-14', 3, 2),
  (4, 'Anfield', 'Anfield', 'Liverpool', 53394, '1884-01-01', 4, 3),
  (5, 'Allianz Arena', 'Allianz', 'Munique', 75024, '2005-05-30', 6, 5)
ON CONFLICT (id) DO NOTHING;

-- 6. Inserir partidas
INSERT INTO partidas (
  id, competicao_id, clube_casa_id, clube_visitante_id, 
  data_partida, rodada, temporada, 
  gols_casa, gols_visitante, status, estadio_id
)
VALUES 
  (1, 1, 1, 2, CURRENT_DATE - INTERVAL '7 days', '1ª Rodada', '2024', 2, 1, 'Finalizada', 1),
  (2, 2, 2, 3, CURRENT_DATE - INTERVAL '5 days', 'Jogo 10', '2023/2024', 1, 1, 'Finalizada', 2),
  (3, 1, 1, 4, CURRENT_DATE + INTERVAL '3 days', '2ª Rodada', '2024', NULL, NULL, 'Agendada', 1),
  (4, 2, 5, 3, CURRENT_DATE + INTERVAL '5 days', 'Jogo 11', '2023/2024', NULL, NULL, 'Agendada', 5)
ON CONFLICT (id) DO NOTHING;

-- 7. Inserir estatísticas para partidas finalizadas
INSERT INTO estatisticas_partidas (
  partida_id,
  posse_bola_casa, posse_bola_visitante,
  finalizacoes_totais_casa, finalizacoes_totais_visitante,
  finalizacoes_no_alvo_casa, finalizacoes_no_alvo_visitante,
  defesas_casa, defesas_visitante,
  escanteios_casa, escanteios_visitante,
  faltas_casa, faltas_visitante,
  impedimentos_casa, impedimentos_visitante,
  tiro_meta_casa, tiro_meta_visitante,
  defesas_do_goleiro_casa, defesas_do_goleiro_visitante,
  cartoes_amarelos_casa, cartoes_amarelos_visitante,
  cartoes_vermelhos_casa, cartoes_vermelhos_visitante
)
VALUES 
  (1, 55, 45, 15, 10, 7, 4, 3, 5, 6, 4, 12, 14, 2, 1, 4, 5, 4, 3, 2, 1, 0, 0),
  (2, 48, 52, 12, 14, 5, 6, 5, 4, 5, 7, 10, 12, 1, 3, 6, 4, 6, 5, 3, 4, 0, 1)
ON CONFLICT (partida_id) DO NOTHING;

-- 8. Verificar inserções
SELECT 'paises_clubes' AS tabela, COUNT(*) AS total FROM paises_clubes
UNION ALL
SELECT 'competicoes' AS tabela, COUNT(*) AS total FROM competicoes
UNION ALL
SELECT 'clubes' AS tabela, COUNT(*) AS total FROM clubes
UNION ALL
SELECT 'estadios' AS tabela, COUNT(*) AS total FROM estadios
UNION ALL
SELECT 'partidas' AS tabela, COUNT(*) AS total FROM partidas
UNION ALL
SELECT 'estatisticas_partidas' AS tabela, COUNT(*) AS total FROM estatisticas_partidas;
