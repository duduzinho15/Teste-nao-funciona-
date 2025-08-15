"""
Simple script to check the posts_redes_sociais table structure.
"""
from sqlalchemy import create_engine, MetaData, Table, inspect
from Coleta_de_dados.database.config import DatabaseSettings

def main():
    try:
        # Initialize database settings and engine
        settings = DatabaseSettings()
        engine = create_engine(settings.database_url)
        
        # Connect to the database
        with engine.connect() as conn:
            # Check if table exists
            inspector = inspect(engine)
            if 'posts_redes_sociais' not in inspector.get_table_names():
                print("❌ Error: 'posts_redes_sociais' table does not exist")
                return
                
            print("✅ Table 'posts_redes_sociais' exists")
            
            # Get columns information
            print("\n📋 Table structure:")
            result = conn.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'posts_redes_sociais'
                ORDER BY ordinal_position
            """)
            
            for row in result:
                print(f"- {row.column_name}: {row.data_type} "
                      f"{'NULL' if row.is_nullable == 'YES' else 'NOT NULL'} "
                      f"{f'DEFAULT {row.column_default}' if row.column_default else ''}")
            
            # Get primary key
            result = conn.execute("""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = 'posts_redes_sociais'::regclass
                AND i.indisprimary;
            """)
            pk_columns = [row[0] for row in result]
            if pk_columns:
                print(f"\n🔑 Primary Key: {', '.join(pk_columns)}")
            
            # Get check constraints
            result = conn.execute("""
                SELECT conname, pg_get_constraintdef(oid)
                FROM pg_constraint 
                WHERE conrelid = 'posts_redes_sociais'::regclass 
                AND contype = 'c';
            """)
            checks = list(result)
            if checks:
                print("\n✅ Check Constraints:")
                for name, definition in checks:
                    print(f"- {name}: {definition}")
            
            # Get unique constraints
            result = conn.execute("""
                SELECT conname, pg_get_constraintdef(oid)
                FROM pg_constraint 
                WHERE conrelid = 'posts_redes_sociais'::regclass 
                AND contype = 'u';
            """)
            uniques = list(result)
            if uniques:
                print("\n🔒 Unique Constraints:")
                for name, definition in uniques:
                    print(f"- {name}: {definition}")
            
            print("\n✅ Database check completed successfully")
            
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
