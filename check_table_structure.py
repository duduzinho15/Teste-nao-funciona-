"""
Script to check the structure of the posts_redes_sociais table.
"""
from Coleta_de_dados.database.config import SessionLocal
from sqlalchemy import text

print("Verificando estrutura das tabelas existentes...")
try:
    db = SessionLocal()
    
    # Verificar estrutura da tabela clubes
    result = db.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'clubes'
        ORDER BY ordinal_position;
    """))
    
    print("\n📋 Estrutura da tabela 'clubes':")
    print("-" * 80)
    for row in result.fetchall():
        nullable = "NULL" if row[2] == "YES" else "NOT NULL"
        default = f" DEFAULT {row[3]}" if row[3] else ""
        print(f"  {row[0]:<20} {row[1]:<15} {nullable:<10}{default}")
    
    # Verificar estrutura da tabela partidas
    result = db.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'partidas'
        ORDER BY ordinal_position;
    """))
    
    print("\n📋 Estrutura da tabela 'partidas':")
    print("-" * 80)
    for row in result.fetchall():
        nullable = "NULL" if row[2] == "YES" else "NOT NULL"
        default = f" DEFAULT {row[3]}" if row[3] else ""
        print(f"  {row[0]:<20} {row[1]:<15} {nullable:<10}{default}")
    
    db.close()
    
except Exception as e:
    print(f"❌ Erro ao verificar estrutura: {e}")
    raise
