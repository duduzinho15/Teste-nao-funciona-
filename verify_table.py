#!/usr/bin/env python3
"""
Script para verificar se a tabela posts_redes_sociais foi criada com sucesso
"""
import psycopg2

# Configurações de conexão
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'apostapro_db',
    'user': 'apostapro_user',
    'password': 'senha_segura_123'
}

def main():
    print("🔍 Verificando a tabela 'posts_redes_sociais'...")
    
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Verifica se a tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'posts_redes_sociais'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ A tabela 'posts_redes_sociais' foi criada com sucesso!")
            
            # Lista as colunas da tabela
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'posts_redes_sociais';
            """)
            
            print("\n📋 Colunas da tabela 'posts_redes_sociais':")
            for col_name, data_type in cursor.fetchall():
                print(f"- {col_name} ({data_type})")
            
            # Verifica índices
            cursor.execute("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'posts_redes_sociais';
            """)
            
            indexes = cursor.fetchall()
            if indexes:
                print("\n🔍 Índices da tabela 'posts_redes_sociais':")
                for idx_name, idx_def in indexes:
                    print(f"- {idx_name}")
                    print(f"  {idx_def}")
            else:
                print("\nℹ️  Nenhum índice encontrado na tabela 'posts_redes_sociais'.")
            
            # Verifica restrições
            cursor.execute("""
                SELECT conname, pg_get_constraintdef(oid)
                FROM pg_constraint
                WHERE conrelid = 'posts_redes_sociais'::regclass;
            """)
            
            constraints = cursor.fetchall()
            if constraints:
                print("\n🔒 Restrições da tabela 'posts_redes_sociais':")
                for con_name, con_def in constraints:
                    print(f"- {con_name}: {con_def}")
            else:
                print("\nℹ️  Nenhuma restrição encontrada na tabela 'posts_redes_sociais'.")
            
        else:
            print("❌ A tabela 'posts_redes_sociais' NÃO foi criada.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar a tabela: {e}")

if __name__ == "__main__":
    main()
