-- Script para configurar o banco de dados e usuário do ApostaPro

-- 1. Criar usuário se não existir
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

-- 2. Criar banco de dados se não existir
SELECT 'Criando banco de dados apostapro_db...' AS mensagem;

SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'apostapro_db'
  AND pid <> pg_backend_pid();

SELECT 'Finalizando conexões com o banco de dados apostapro_db...' AS mensagem;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'apostapro_db') THEN
        CREATE DATABASE apostapro_db
        WITH 
        OWNER = postgres
        ENCODING = 'UTF8'
        LC_COLLATE = 'Portuguese_Brazil.1252'
        LC_CTYPE = 'Portuguese_Brazil.1252'
        TABLESPACE = pg_default
        CONNECTION LIMIT = -1
        TEMPLATE template0;
        
        RAISE NOTICE 'Banco de dados apostapro_db criado com sucesso';
    ELSE
        RAISE NOTICE 'Banco de dados apostapro_db já existe';
    END IF;
END
$$;

-- 3. Conceder privilégios ao usuário
\c apostapro_db

GRANT ALL PRIVILEGES ON DATABASE apostapro_db TO apostapro_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO apostapro_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO apostapro_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO apostapro_user;

-- 4. Verificar se o usuário tem permissões corretas
SELECT 'Verificando permissões do usuário apostapro_user...' AS mensagem;

SELECT 
    r.rolname, 
    r.rolsuper, 
    r.rolinherit, 
    r.rolcreaterole, 
    r.rolcreatedb, 
    r.rolcanlogin
FROM 
    pg_roles r 
WHERE 
    r.rolname = 'apostapro_user';

-- 5. Verificar se o banco de dados foi criado corretamente
SELECT 'Verificando banco de dados criado...' AS mensagem;

SELECT 
    datname, 
    pg_encoding_to_char(encoding) AS encoding,
    datcollate, 
    datctype 
FROM 
    pg_database 
WHERE 
    datname = 'apostapro_db';
