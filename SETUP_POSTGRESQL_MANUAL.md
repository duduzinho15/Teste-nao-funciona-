# CONFIGURAÇÃO MANUAL DO POSTGRESQL
## Para finalizar a migração do ApostaPro

### 🔧 PASSO 1: Configurar Banco de Dados

Abra o **pgAdmin** ou **SQL Shell (psql)** e execute os seguintes comandos:

```sql
-- 1. Conectar como postgres (usuário padrão)
-- Senha: a que você definiu durante a instalação

-- 2. Criar banco de dados
CREATE DATABASE apostapro_db;

-- 3. Criar usuário específico (opcional, pode usar postgres)
CREATE USER apostapro_user WITH PASSWORD 'apostapro_pass';

-- 4. Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE apostapro_db TO apostapro_user;

-- 5. Conectar ao banco criado
\c apostapro_db

-- 6. Conceder privilégios no schema
GRANT ALL ON SCHEMA public TO apostapro_user;
```

### 🔧 PASSO 2: Atualizar Arquivo .env

Edite o arquivo `.env` com suas credenciais:

```env
# PostgreSQL Configuration
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/apostapro_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=apostapro_db
DB_USER=postgres
DB_PASSWORD=SUA_SENHA
```

### 🔧 PASSO 3: Executar Migração

```bash
# Testar conexão
python -c "from Coleta_de_dados.database import db_manager; print('Resultado:', db_manager.test_connection())"

# Executar migração
python migrate_to_postgresql.py

# Testar sistema completo
python teste_sistema_orm.py
```

### 🔧 PASSO 4: Verificar Tabelas

```bash
# Verificar tabelas criadas
python verificar_tabelas_fbref_orm.py
```

### ✅ RESULTADO ESPERADO

- ✅ Conexão PostgreSQL estabelecida
- ✅ Schema criado com SQLAlchemy
- ✅ Todos os testes passando
- ✅ Sistema 100% em PostgreSQL + ORM
