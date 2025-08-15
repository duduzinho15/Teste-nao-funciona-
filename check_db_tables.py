"""
Script to check database tables and verify the posts_redes_sociais table exists.
"""
from sqlalchemy import inspect
from Coleta_de_dados.database.config import db_manager

def check_tables():
    # Get the SQLAlchemy engine
    engine = db_manager.engine
    
    # Create an inspector
    inspector = inspect(engine)
    
    # Get all table names
    tables = inspector.get_table_names()
    print("\n📋 TABLES IN THE DATABASE:")
    for table in sorted(tables):
        print(f"- {table}")
    
    # Check if posts_redes_sociais table exists
    if 'posts_redes_sociais' in tables:
        print("\n✅ Table 'posts_redes_sociais' exists!")
        
        # Get columns info
        columns = inspector.get_columns('posts_redes_sociais')
        print("\n📊 COLUMNS IN 'posts_redes_sociais':")
        for col in columns:
            print(f"- {col['name']}: {col['type']} {'(PK)' if col.get('primary_key') else ''} {'(Nullable)' if col.get('nullable') else ''}")
    else:
        print("\n❌ Table 'posts_redes_sociais' does NOT exist!")

if __name__ == "__main__":
    print("🔍 CHECKING DATABASE TABLES...")
    check_tables()
