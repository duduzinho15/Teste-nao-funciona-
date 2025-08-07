-- Script para criar um novo banco de dados com encoding correto
-- Execute como: psql -U postgres -f criar_banco_utf8.sql

-- Encerrar conexões ativas ao banco antigo (se existir)
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'apostapro_utf8';

-- Remover o banco se já existir
DROP DATABASE IF EXISTS apostapro_utf8;

-- Criar um novo banco de dados com encoding correto
CREATE DATABASE apostapro_utf8 
WITH 
ENCODING = 'UTF8'
LC_COLLATE = 'Portuguese_Brazil.1252'
LC_CTYPE = 'Portuguese_Brazil.1252'
TEMPLATE = template0;

-- Conectar ao novo banco
\c apostapro_utf8

-- Criar extensão se necessário
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE apostapro_utf8 TO postgres;

-- Verificar configurações
\l+ apostapro_utf8

-- Mensagem de conclusão
\echo '✅ Banco de dados apostapro_utf8 criado com sucesso com encoding UTF8!'
