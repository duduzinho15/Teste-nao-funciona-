-- Verificar se o banco de dados existe
SELECT 'Database apostapro_db exists: ' || 
       CASE WHEN EXISTS (SELECT 1 FROM pg_database WHERE datname = 'apostapro_db') 
            THEN 'YES' ELSE 'NO' END;

-- Verificar se o usuário existe
SELECT 'User apostapro_user exists: ' || 
       CASE WHEN EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'apostapro_user') 
            THEN 'YES' ELSE 'NO' END;
