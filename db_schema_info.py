"""
Script para obter informações detalhadas sobre o esquema do banco de dados.
"""
import psycopg2
from psycopg2 import sql

def get_db_connection():
    """Estabelece conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="apostapro_db",
            user="postgres",
            password="postgres",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def get_table_columns(conn, table_name):
    """Obtém informações sobre as colunas de uma tabela."""
    query = """
    SELECT 
        column_name, 
        data_type, 
        is_nullable,
        column_default,
        character_maximum_length,
        numeric_precision,
        numeric_scale
    FROM 
        information_schema.columns
    WHERE 
        table_name = %s
    ORDER BY 
        ordinal_position;
    """
    
    with conn.cursor() as cur:
        cur.execute(query, (table_name,))
        return cur.fetchall()

def get_foreign_keys(conn, table_name):
    """Obtém informações sobre as chaves estrangeiras de uma tabela."""
    query = """
    SELECT
        tc.constraint_name,
        kcu.column_name, 
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name 
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
    WHERE 
        tc.constraint_type = 'FOREIGN KEY' 
        AND tc.table_name = %s;
    """
    
    with conn.cursor() as cur:
        cur.execute(query, (table_name,))
        return cur.fetchall()

def get_primary_keys(conn, table_name):
    """Obtém informações sobre a chave primária de uma tabela."""
    query = """
    SELECT
        kcu.column_name
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
    WHERE 
        tc.constraint_type = 'PRIMARY KEY' 
        AND tc.table_name = %s;
    """
    
    with conn.cursor() as cur:
        cur.execute(query, (table_name,))
        return [row[0] for row in cur.fetchall()]

def get_table_data_count(conn, table_name):
    """Obtém a contagem de registros em uma tabela."""
    query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name))
    
    with conn.cursor() as cur:
        try:
            cur.execute(query)
            return cur.fetchone()[0]
        except:
            return 0

def print_table_info(conn, table_name):
    """Exibe informações detalhadas sobre uma tabela."""
    print(f"\n{'='*80}")
    print(f"TABELA: {table_name}")
    print(f"{'='*80}")
    
    # Obtém informações das colunas
    columns = get_table_columns(conn, table_name)
    if not columns:
        print("Tabela não encontrada ou sem colunas.")
        return
    
    # Exibe informações das colunas
    print("\nCOLUNAS:")
    print("-" * 80)
    print(f"{'Nome':<30} {'Tipo':<20} {'Nulo?':<8} {'Padrão':<20} {'Tamanho/Precisão'}")
    print("-" * 80)
    
    for col in columns:
        col_name, data_type, is_nullable, col_default, char_max_len, num_precision, num_scale = col
        
        # Formata o tipo de dados com informações adicionais, se disponíveis
        type_info = data_type
        if char_max_len:
            type_info += f"({char_max_len})"
        elif num_precision is not None:
            if num_scale is not None and num_scale > 0:
                type_info += f"({num_precision},{num_scale})"
            else:
                type_info += f"({num_precision})"
        
        # Formata o valor padrão
        default_str = str(col_default) if col_default is not None else ""
        
        print(f"{col_name:<30} {type_info:<20} {'SIM' if is_nullable == 'YES' else 'NÃO':<8} {default_str:<20}")
    
    # Obtém informações sobre chaves primárias
    pks = get_primary_keys(conn, table_name)
    if pks:
        print("\nCHAVE PRIMÁRIA:")
        print("-" * 80)
        print(", ".join(pks))
    
    # Obtém informações sobre chaves estrangeiras
    fks = get_foreign_keys(conn, table_name)
    if fks:
        print("\nCHAVES ESTRANGEIRAS:")
        print("-" * 80)
        for fk in fks:
            constraint_name, column_name, foreign_table, foreign_column = fk
            print(f"{column_name} -> {foreign_table}({foreign_column})")
    
    # Obtém a contagem de registros
    count = get_table_data_count(conn, table_name)
    print(f"\nTOTAL DE REGISTROS: {count}")

def list_all_tables(conn):
    """Lista todas as tabelas no banco de dados."""
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """
    
    with conn.cursor() as cur:
        cur.execute(query)
        return [row[0] for row in cur.fetchall()]

def main():
    # Estabelece conexão com o banco de dados
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Lista todas as tabelas
        print("🔍 Conectado ao banco de dados. Obtendo informações...")
        tables = list_all_tables(conn)
        
        if not tables:
            print("Nenhuma tabela encontrada no esquema público.")
            return
        
        print(f"\n📋 TABELAS ENCONTRADAS ({len(tables)}):")
        print("=" * 80)
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        
        # Exibe informações detalhadas para cada tabela
        for table in tables:
            print_table_info(conn, table)
        
    except Exception as e:
        print(f"Erro ao obter informações do banco de dados: {e}")
    finally:
        conn.close()
        print("\n🔒 Conexão com o banco de dados encerrada.")

if __name__ == "__main__":
    main()
