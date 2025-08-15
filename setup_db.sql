-- Script para configurar o banco de dados e inserir dados iniciais

-- 1. Criar banco de dados (executar separadamente no psql)
-- CREATE DATABASE apostapro_db 
-- WITH ENCODING='UTF8' 
-- LC_COLLATE='pt_BR.UTF-8' 
-- LC_CTYPE='pt_BR.UTF-8' 
-- TEMPLATE=template0;

-- 2. Criar usuário e conceder privilégios
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'apostapro_user') THEN
        CREATE USER apostapro_user WITH PASSWORD 'senha_segura_123';
    END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE apostapro_db TO apostapro_user;

-- Conectar ao banco de dados
\c apostapro_db

-- 3. Criar extensão se não existir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 4. Inserir países
INSERT INTO paises_clubes (id, nome, codigo_iso, continente)
VALUES 
  (1, 'Brasil', 'BRA', 'América do Sul'),
  (2, 'Espanha', 'ESP', 'Europa'),
  (3, 'Inglaterra', 'ENG', 'Europa')
ON CONFLICT (id) DO NOTHING;

-- 5. Inserir competições
INSERT INTO competicoes (id, nome, nome_curto, tipo, pais, nivel)
VALUES 
  (1, 'Campeonato Brasileiro Série A', 'Brasileirão', 'Liga', 'Brasil', 'A'),
  (2, 'La Liga', 'LaLiga', 'Liga', 'Espanha', 'A')
ON CONFLICT (id) DO NOTHING;

-- 6. Inserir clubes
INSERT INTO clubes (id, nome, abreviacao, pais_id, cidade, fundacao)
VALUES 
  (1, 'Flamengo', 'FLA', 1, 'Rio de Janeiro', '1895-11-15'),
  (2, 'Barcelona', 'BAR', 2, 'Barcelona', '1899-11-29'),
  (3, 'Real Madrid', 'RMA', 2, 'Madrid', '1902-03-06')
ON CONFLICT (id) DO NOTHING;

-- 7. Criar tabela de estádios se não existir
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

-- 8. Inserir estádios
INSERT INTO estadios (id, nome, apelido, cidade, capacidade, 
                     inauguracao, gramado, clube_id, pais_id, ativo)
VALUES 
  (1, 'Maracanã', 'Maraca', 'Rio de Janeiro', 78838, 
   '1950-06-16', 'Natural', 1, 1, TRUE),
  (2, 'Camp Nou', 'Camp Nou', 'Barcelona', 99354, 
   '1957-09-24', 'Natural', 2, 2, TRUE),
  (3, 'Santiago Bernabéu', 'Bernabéu', 'Madrid', 81044, 
   '1947-12-14', 'Híbrido', 3, 2, TRUE)
ON CONFLICT (id) DO NOTHING;

-- 9. Inserir partidas
INSERT INTO partidas (
    id, competicao_id, clube_casa_id, clube_visitante_id, 
    data_partida, rodada, temporada, 
    gols_casa, gols_visitante, status, estadio_id
)
VALUES 
  (1, 1, 1, 2, CURRENT_DATE - INTERVAL '7 days', 
   '1ª Rodada', '2024', 2, 1, 'Finalizada', 1),
  (2, 2, 2, 3, CURRENT_DATE - INTERVAL '5 days', 
   'Jogo 10', '2023/2024', 1, 1, 'Finalizada', 2),
  (3, 1, 1, 3, CURRENT_DATE + INTERVAL '3 days', 
   '2ª Rodada', '2024', NULL, NULL, 'Agendada', 1)
ON CONFLICT (id) DO NOTHING;

-- 10. Verificar dados inseridos
\echo '\nDados inseridos:'
SELECT 'paises_clubes' AS tabela, COUNT(*) AS total FROM paises_clubes
UNION ALL
SELECT 'clubes' AS tabela, COUNT(*) FROM clubes
UNION ALL
SELECT 'competicoes' AS tabela, COUNT(*) FROM competicoes
UNION ALL
SELECT 'estadios' AS tabela, COUNT(*) FROM estadios
UNION ALL
SELECT 'partidas' AS tabela, COUNT(*) FROM partidas;
