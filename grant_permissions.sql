-- Conceder permissões ao usuário apostapro_user no esquema public
\c apostapro_db

-- Conceder todas as permissões no esquema public
GRANT ALL ON SCHEMA public TO apostapro_user;

-- Conceder permissões em todas as tabelas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO apostapro_user;

-- Conceder permissões em todas as sequências
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO apostapro_user;

-- Conceder permissões em todas as funções
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO apostapro_user;

-- Conceder permissões para operações futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO apostapro_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO apostapro_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO apostapro_user;

-- Verificar permissões concedidas
\dn+ public
\dp
\du apostapro_user
