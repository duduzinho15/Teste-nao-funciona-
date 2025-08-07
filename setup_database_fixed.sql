-- Script para configurar o banco de dados e usuário do ApostaPro com encoding correto

-- 1. Definir encoding para UTF-8 explicitamente
SET client_encoding = 'UTF8';

-- 2. Criar usuário se não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'apostapro_user') THEN
        CREATE USER apostapro_user WITH PASSWORD 'senha_segura_123';
        RAISE NOTICE 'Usuário apostapro_user criado com sucesso';
    ELSE
        RAISE NOTICE 'Usuário apostapro_user já existe';
    END IF;
END
$$;

-- 3. Encerrar todas as conexões com o banco de dados existente (se houver)
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'apostapro_db'
  AND pid <> pg_backend_pid();

-- 4. Remover o banco de dados se ele existir
DROP DATABASE IF EXISTS apostapro_db;

-- 5. Criar o banco de dados com encoding UTF-8
CREATE DATABASE apostapro_db
WITH 
OWNER = postgres
ENCODING = 'UTF8'
LC_COLLATE = 'Portuguese_Brazil.1252'
LC_CTYPE = 'Portuguese_Brazil.1252'
TABLESPACE = pg_default
CONNECTION LIMIT = -1
TEMPLATE template0;

-- 6. Conectar ao banco de dados recém-criado
\c apostapro_db

-- 7. Definir encoding para a sessão atual
SET client_encoding = 'UTF8';

-- 8. Criar extensão para UUID se não existir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 9. Conceder privilégios ao usuário
GRANT ALL PRIVILEGES ON DATABASE apostapro_db TO apostapro_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO apostapro_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO apostapro_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO apostapro_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO apostapro_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO apostapro_user;

-- 10. Verificar configurações do banco de dados
SELECT 
    datname, 
    pg_encoding_to_char(encoding) AS encoding,
    datcollate, 
    datctype 
FROM 
    pg_database 
WHERE 
    datname = 'apostapro_db';

-- 11. Verificar usuário e permissões
\du apostapro_user
