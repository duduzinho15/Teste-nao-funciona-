-- Verificar a codificação do banco de dados
SELECT 
    datname AS "Database", 
    pg_encoding_to_char(encoding) AS "Encoding",
    datcollate AS "Collation",
    datctype AS "Character Type"
FROM 
    pg_database 
WHERE 
    datname = 'apostapro_db';

-- Verificar as configurações de codificação do servidor
SHOW server_encoding;
SHOW client_encoding;
SHOW lc_collate;
SHOW lc_ctype;

-- Verificar as tabelas e suas codificações
SELECT 
    t.tablename AS "Table",
    c.reloptions AS "Storage Parameters"
FROM 
    pg_tables t
    JOIN pg_class c ON t.tablename = c.relname
WHERE 
    t.schemaname = 'public';
