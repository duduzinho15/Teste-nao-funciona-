"""
Direct SQL query to check the posts_redes_sociais table structure.
"""
import psycopg2
from Coleta_de_dados.database.config import DatabaseSettings

def main():
    try:
        # Get database settings
        settings = DatabaseSettings()
        
        # Connect to the database
        conn = psycopg2.connect(
            host=settings.db_host,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            port=settings.db_port
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'posts_redes_sociais'
            );
        """)
        
        if not cur.fetchone()[0]:
            print("❌ Error: 'posts_redes_sociais' table does not exist")
            return
            
        print("✅ Table 'posts_redes_sociais' exists")
        
        # Get table structure
        print("\n📋 Table structure:")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'posts_redes_sociais'
            ORDER BY ordinal_position;
        """)
        
        for row in cur.fetchall():
            print(f"- {row[0]}: {row[1]} {'NULL' if row[2] == 'YES' else 'NOT NULL'} {f'DEFAULT {row[3]}' if row[3] else ''}")
        
        # Get primary key
        cur.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = 'posts_redes_sociais'::regclass
            AND i.indisprimary;
        """)
        
        pk_columns = [row[0] for row in cur.fetchall()]
        if pk_columns:
            print(f"\n🔑 Primary Key: {', '.join(pk_columns)}")
        
        # Get check constraints
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid)
            FROM pg_constraint 
            WHERE conrelid = 'posts_redes_sociais'::regclass 
            AND contype = 'c';
        """)
        
        checks = cur.fetchall()
        if checks:
            print("\n✅ Check Constraints:")
            for name, definition in checks:
                print(f"- {name}: {definition}")
        
        # Get unique constraints
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid)
            FROM pg_constraint 
            WHERE conrelid = 'posts_redes_sociais'::regclass 
            AND contype = 'u';
        """)
        
        uniques = cur.fetchall()
        if uniques:
            print("\n🔒 Unique Constraints:")
            for name, definition in uniques:
                print(f"- {name}: {definition}")
        
        print("\n✅ Database check completed successfully")
        
        # Close communication with the database
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
