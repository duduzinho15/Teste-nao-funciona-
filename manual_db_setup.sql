-- Script para configurar manualmente o banco de dados do ApostaPro
-- Este script deve ser executado como superusuário (postgres)

-- 1. Encerrar todas as conexões ativas com o banco de dados
-- Este comando será executado separadamente
-- SELECT pg_terminate_backend(pg_stat_activity.pid)
-- FROM pg_stat_activity
-- WHERE pg_stat_activity.datname = 'apostapro_db'
-- AND pid <> pg_backend_pid();

-- 2. Remover o banco de dados existente (se houver)
-- Este comando será executado separadamente
-- DROP DATABASE IF EXISTS apostapro_db;

-- 3. Criar um novo banco de dados com codificação UTF-8
-- Este comando será executado separadamente
-- CREATE DATABASE apostapro_db
-- WITH 
-- ENCODING = 'UTF8'
-- LC_COLLATE = 'Portuguese_Brazil.1252'
-- LC_CTYPE = 'Portuguese_Brazil.1252'
-- TEMPLATE = template0;

-- 4. O banco de dados já deve estar criado e a conexão já deve estar nele

-- 5. Criar extensão para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 6. Criar usuário e conceder privilégios
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'apostapro_user') THEN
        CREATE USER apostapro_user WITH PASSWORD 'senha_segura_123';
    END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE apostapro_db TO apostapro_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO apostapro_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO apostapro_user;

-- 7. Criar tabelas principais

-- Tabela de países
CREATE TABLE IF NOT EXISTS paises_clubes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    codigo_iso CHAR(3) UNIQUE,
    continente VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de competições
CREATE TABLE IF NOT EXISTS competicoes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    nome_curto VARCHAR(50),
    tipo VARCHAR(50),
    pais VARCHAR(100),
    nivel VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de clubes
CREATE TABLE IF NOT EXISTS clubes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    abreviacao VARCHAR(20),
    pais_id INTEGER REFERENCES paises_clubes(id) ON DELETE SET NULL,
    cidade VARCHAR(100),
    fundacao DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_clube_nome UNIQUE (nome)
);

-- Tabela de estádios
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

-- Tabela de partidas
CREATE TABLE IF NOT EXISTS partidas (
    id SERIAL PRIMARY KEY,
    competicao_id INTEGER REFERENCES competicoes(id) ON DELETE SET NULL,
    clube_casa_id INTEGER REFERENCES clubes(id) ON DELETE SET NULL,
    clube_visitante_id INTEGER REFERENCES clubes(id) ON DELETE SET NULL,
    data_partida TIMESTAMP WITH TIME ZONE,
    rodada VARCHAR(50),
    temporada VARCHAR(20),
    gols_casa INTEGER,
    gols_visitante INTEGER,
    status VARCHAR(50),
    estadio_id INTEGER REFERENCES estadios(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Inserir dados iniciais

-- Inserir países
INSERT INTO paises_clubes (id, nome, codigo_iso, continente)
VALUES 
  (1, 'Brasil', 'BRA', 'América do Sul'),
  (2, 'Espanha', 'ESP', 'Europa'),
  (3, 'Inglaterra', 'ENG', 'Europa')
ON CONFLICT (id) DO NOTHING;

-- Inserir competições
INSERT INTO competicoes (id, nome, nome_curto, tipo, pais, nivel)
VALUES 
  (1, 'Campeonato Brasileiro Série A', 'Brasileirão', 'Liga', 'Brasil', 'A'),
  (2, 'La Liga', 'LaLiga', 'Liga', 'Espanha', 'A')
ON CONFLICT (id) DO NOTHING;

-- Inserir clubes
INSERT INTO clubes (id, nome, abreviacao, pais_id, cidade, fundacao)
VALUES 
  (1, 'Flamengo', 'FLA', 1, 'Rio de Janeiro', '1895-11-15'),
  (2, 'Barcelona', 'BAR', 2, 'Barcelona', '1899-11-29'),
  (3, 'Real Madrid', 'RMA', 2, 'Madrid', '1902-03-06')
ON CONFLICT (id) DO NOTHING;

-- Inserir estádios
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

-- Inserir partidas
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

-- 9. Verificar dados inseridos
SELECT 'Dados inseridos:' AS mensagem;

SELECT 'paises_clubes' AS tabela, COUNT(*) AS total FROM paises_clubes
UNION ALL
SELECT 'clubes' AS tabela, COUNT(*) FROM clubes
UNION ALL
SELECT 'competicoes' AS tabela, COUNT(*) FROM competicoes
UNION ALL
SELECT 'estadios' AS tabela, COUNT(*) FROM estadios
UNION ALL
SELECT 'partidas' AS tabela, COUNT(*) FROM partidas;

-- 10. Conceder permissões ao usuário da aplicação
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO apostapro_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO apostapro_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO apostapro_user;

SELECT '✅ Configuração do banco de dados concluída com sucesso!' AS mensagem;
SELECT '✅ Você pode agora executar a API e testar o endpoint /matches' AS mensagem;
