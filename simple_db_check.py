import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

def check_database():
    print("=== Simple Database Check ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Database connection parameters
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'apostapro_db'),
        'user': os.getenv('DB_USER', 'apostapro_user'),
        'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
    }
    
    try:
        # Connect to the database
        print(f"Connecting to database: {db_params['database']} on {db_params['host']}:{db_params['port']}")
        conn = psycopg2.connect(**db_params)
        
        # Create a cursor
        cur = conn.cursor()
        
        # Check PostgreSQL version
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"\n✅ PostgreSQL Version: {db_version[0]}")
        
        # Check if alembic_version table exists
        try:
            cur.execute("SELECT * FROM alembic_version;")
            alembic_version = cur.fetchone()
            print(f"✅ Alembic Version: {alembic_version[0]}")
        except Exception as e:
            print(f"❌ Error checking alembic_version: {e}")
        
        # List all tables in the public schema
        print("\nListing all tables in the public schema:")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        if tables:
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("No tables found in the public schema.")
        
        # Close communication with the database
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure PostgreSQL is running")
        print("2. Verify the database and user exist")
        print("3. Check the password is correct")
        print("4. Ensure PostgreSQL is configured to accept TCP/IP connections")
        print("5. Check pg_hba.conf for proper authentication settings")

if __name__ == "__main__":
    check_database()
