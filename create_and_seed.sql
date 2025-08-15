-- Script para criar a tabela 'estadios' e popular com dados de teste

-- 1. Criar a tabela estadios (se não existir)
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

-- 2. Inserir dados mínimos (se não existirem)
-- Países
INSERT INTO paises_clubes (id, nome, codigo_iso, continente)
VALUES 
  (1, 'Brasil', 'BRA', 'América do Sul'),
  (2, 'Espanha', 'ESP', 'Europa'),
  (3, 'Inglaterra', 'ENG', 'Europa')
ON CONFLICT (id) DO NOTHING;

-- Competições
INSERT INTO competicoes (id, nome, nome_curto, tipo, pais, nivel)
VALUES 
  (1, 'Campeonato Brasileiro Série A', 'Brasileirão', 'Liga', 'Brasil', 'A'),
  (2, 'La Liga', 'LaLiga', 'Liga', 'Espanha', 'A')
ON CONFLICT (id) DO NOTHING;

-- Clubes
INSERT INTO clubes (id, nome, abreviacao, pais_id, cidade, fundacao)
VALUES 
  (1, 'Flamengo', 'FLA', 1, 'Rio de Janeiro', '1895-11-15'),
  (2, 'Barcelona', 'BAR', 2, 'Barcelona', '1899-11-29'),
  (3, 'Real Madrid', 'RMA', 2, 'Madrid', '1902-03-06')
ON CONFLICT (id) DO NOTHING;

-- Estádios
INSERT INTO estadios (id, nome, apelido, cidade, capacidade, inauguracao, clube_id, pais_id)
VALUES 
  (1, 'Maracanã', 'Maraca', 'Rio de Janeiro', 78838, '1950-06-16', 1, 1),
  (2, 'Camp Nou', 'Camp Nou', 'Barcelona', 99354, '1957-09-24', 2, 2),
  (3, 'Santiago Bernabéu', 'Bernabéu', 'Madrid', 81044, '1947-12-14', 3, 2)
ON CONFLICT (id) DO NOTHING;

-- Partidas
INSERT INTO partidas (
  id, competicao_id, clube_casa_id, clube_visitante_id, 
  data_partida, rodada, temporada, 
  gols_casa, gols_visitante, status, estadio_id
)
VALUES 
  (1, 1, 1, 2, CURRENT_DATE - INTERVAL '7 days', '1ª Rodada', '2024', 2, 1, 'Finalizada', 1),
  (2, 2, 2, 3, CURRENT_DATE - INTERVAL '5 days', 'Jogo 10', '2023/2024', 1, 1, 'Finalizada', 2),
  (3, 1, 1, 3, CURRENT_DATE + INTERVAL '3 days', '2ª Rodada', '2024', NULL, NULL, 'Agendada', 1)
ON CONFLICT (id) DO NOTHING;

-- Verificar contagem de registros
SELECT 'paises_clubes' AS tabela, COUNT(*) AS total FROM paises_clubes
UNION ALL
SELECT 'competicoes' AS tabela, COUNT(*) AS total FROM competicoes
UNION ALL
SELECT 'clubes' AS tabela, COUNT(*) AS total FROM clubes
UNION ALL
SELECT 'estadios' AS tabela, COUNT(*) AS total FROM estadios
UNION ALL
SELECT 'partidas' AS tabela, COUNT(*) AS total FROM partidas;
