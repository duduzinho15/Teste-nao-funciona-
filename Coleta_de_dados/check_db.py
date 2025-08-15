import sqlite3
import sys
from pathlib import Path

def print_table_info(conn, table_name):
    """Exibe informações detalhadas sobre uma tabela."""
    cursor = conn.cursor()
    
    try:
        # Obtém informações sobre as colunas
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n=== Estrutura da tabela {table_name} ===")
        print("-" * 60)
        print("ID | Nome                | Tipo         | Pode ser nulo | Valor padrão | É chave primária")
        print("-" * 60)
        
        for col in columns:
            col_id, name, col_type, not_null, default_val, is_pk = col
            nullable = "SIM" if not not_null else "NÃO"
            default_val = default_val if default_val is not None else "NULL"
            print(f"{col_id:<3} | {name:<19} | {col_type:<12} | {nullable:<13} | {str(default_val):<13} | {bool(is_pk)}")
        
        # Conta o número de registros
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\nTotal de registros: {count}")
        
        # Se houver registros, exibe alguns exemplos
        if count > 0:
            print("\nPrimeiros 3 registros:")
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            col_names = [desc[0] for desc in cursor.description]
            print(" | ".join(f"{name:<15}" for name in col_names))
            print("-" * 100)
            for row in cursor.fetchall():
                print(" | ".join(f"{str(val)[:15]:<15}" for val in row))
        
        # Obtém índices
        cursor.execute(f"PRAGMA index_list('{table_name}')")
        indexes = cursor.fetchall()
        
        if indexes:
            print("\nÍndices:")
            for idx in indexes:
                idx_id, idx_name, unique = idx[0], idx[1], bool(idx[2])
                # Obtém as colunas do índice
                cursor.execute(f"PRAGMA index_info('{idx_name}')")
                idx_cols = [col[2] for col in cursor.fetchall()]
                print(f"  - {idx_name}: {idx_cols} (Único: {'SIM' if unique else 'NÃO'})")
        
        # Obtém chaves estrangeiras
        cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
        fks = cursor.fetchall()
        
        if fks:
            print("\nChaves estrangeiras:")
            for fk in fks:
                _, _, ref_table, from_col, to_col, on_update, on_delete, _ = fk
                print(f"  - {from_col} -> {ref_table}({to_col}) [ON DELETE: {on_delete}, ON UPDATE: {on_update}]")
        
        # Obtém a definição SQL completa da tabela
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", 
            (table_name,)
        )
        table_sql = cursor.fetchone()
        
        if table_sql and table_sql[0]:
            print("\nDefinição SQL da tabela:")
            print(table_sql[0])
    
    except sqlite3.Error as e:
        print(f"Erro ao acessar a tabela {table_name}: {e}")
    finally:
        cursor.close()

def main():
    # Caminho para o banco de dados
    db_path = Path("database/football_data.db")
    
    if not db_path.exists():
        print(f"Erro: Arquivo de banco de dados não encontrado em: {db_path}")
        return
    
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        # Lista todas as tabelas
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
        
        tables = cursor.fetchall()
        
        if not tables:
            print("Nenhuma tabela encontrada no banco de dados.")
            return
        
        print(f"\nTabelas encontradas no banco de dados ({len(tables)}):")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table['name']}")
        
        # Verifica se a tabela posts_redes_sociais existe
        target_table = "posts_redes_sociais"
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name=?", 
            (target_table,)
        )
        
        if cursor.fetchone():
            print(f"\n{'='*80}")
            print(f"INFORMAÇÕES DETALHADAS DA TABELA: {target_table}")
            print("="*80)
            print_table_info(conn, target_table)
        else:
            print(f"\nAviso: A tabela '{target_table}' não foi encontrada no banco de dados.")
            print("Tabelas disponíveis:")
            for table in tables:
                print(f"  - {table['name']}")
        
        cursor.close()
        
    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
