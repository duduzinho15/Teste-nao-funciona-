# check_existing_tables.py
from Coleta_de_dados.database.config import SessionLocal
from sqlalchemy import text

print("Verificando tabelas existentes no banco de dados...")
try:
    db = SessionLocal()
    
    # Verificar se a tabela alembic_version existe
    result = db.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'alembic_version'
        );
    """))
    alembic_exists = result.scalar()
    print(f"Tabela alembic_version existe: {alembic_exists}")
    
    # Listar todas as tabelas existentes
    result = db.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """))
    
    tables = [row[0] for row in result.fetchall()]
    print(f"Tabelas existentes ({len(tables)}):")
    for table in tables:
        print(f"  - {table}")
    
    db.close()
    
except Exception as e:
    print(f"❌ Erro ao verificar tabelas: {e}")
    raise
