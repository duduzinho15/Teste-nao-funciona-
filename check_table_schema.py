"""
Script to check the structure of the 'partidas' table and its dependencies.
"""
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

def check_table_structure():
    # Connection string
    conn_str = "postgresql://apostapro_user:senha_segura_123@localhost:5432/apostapro_db"
    
    try:
        print("🔍 Connecting to the database...")
        engine = create_engine(conn_str)
        
        with engine.connect() as conn:
            # Get the inspector to examine the schema
            inspector = inspect(engine)
            
            # Check if the table exists
            if 'partidas' not in inspector.get_table_names():
                print("❌ The 'partidas' table does not exist in the database.")
                return 1
            
            print("\n📋 Structure of the 'partidas' table:")
            print("=" * 50)
            
            # Get the columns of the table
            columns = inspector.get_columns('partidas')
            for column in columns:
                print(f"- {column['name']}: {column['type']} (nullable: {column['nullable']})")
            
            # Check foreign keys
            print("\n🔑 Foreign keys:")
            fks = inspector.get_foreign_keys('partidas')
            if fks:
                for fk in fks:
                    print(f"- {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
            else:
                print("No foreign keys found.")
            
            # Check primary key
            print("\n🔑 Primary key:")
            pk = inspector.get_pk_constraint('partidas')
            if pk['constrained_columns']:
                print(f"- Primary key: {pk['constrained_columns']}")
            else:
                print("No primary key found.")
            
            # Check indexes
            print("\n📊 Indexes:")
            indexes = inspector.get_indexes('partidas')
            if indexes:
                for idx in indexes:
                    print(f"- {idx['name']}: {idx['column_names']} (unique: {idx.get('unique', False)})")
            else:
                print("No indexes found.")
            
            # Count records
            result = conn.execute(text("SELECT COUNT(*) FROM partidas"))
            count = result.scalar()
            print(f"\n📊 Total records in 'partidas': {count}")
            
            # Check for required foreign key constraints
            required_fks = ['clube_casa_id', 'clube_visitante_id', 'competicao_id', 'estadio_id']
            existing_fk_columns = [col for fk in fks for col in fk['constrained_columns']]
            
            missing_fks = [col for col in required_fks if col not in existing_fk_columns]
            
            if missing_fks:
                print(f"\n⚠️  Missing foreign key constraints: {', '.join(missing_fks)}")
            
            return 0
            
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🔍 Starting database schema check for 'partidas' table...")
    sys.exit(check_table_structure())
