"""
Script para verificar restrições e triggers nas tabelas do banco de dados.
"""
import psycopg2

def get_table_constraints():
    """Obtém as restrições das tabelas do banco de dados"""
    # Configurações do banco de dados
    db_config = {
        'host': 'localhost',
        'database': 'apostapro_db',
        'user': 'apostapro_user',
        'password': 'senha_segura_123',
        'port': '5432'
    }
    
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        print("🔍 Verificando restrições nas tabelas...")
        
        # Obtém a lista de tabelas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        
        # Para cada tabela, obtém as restrições e triggers
        for table in tables:
            print(f"\n📋 Tabela: {table}")
            print("=" * 80)
            
            # Obtém as restrições de chave primária
            cur.execute("""
                SELECT kcu.column_name, ccu.table_name AS foreign_table_name,
                       ccu.column_name AS foreign_column_name,
                       tc.constraint_type
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                LEFT JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
                WHERE tc.table_name = %s
                ORDER BY tc.constraint_type, kcu.column_name;
            """, (table,))
            
            constraints = cur.fetchall()
            
            if constraints:
                print("\n🔑 Restrições:")
                for constraint in constraints:
                    col_name, fk_table, fk_col, constr_type = constraint
                    if constr_type == 'PRIMARY KEY':
                        print(f"- Chave primária: {col_name}")
                    elif constr_type == 'FOREIGN KEY':
                        print(f"- Chave estrangeira: {col_name} → {fk_table}({fk_col or '?'})")
                    elif constr_type == 'UNIQUE':
                        print(f"- Único: {col_name}")
                    else:
                        print(f"- {constr_type}: {col_name}")
            else:
                print("ℹ️ Nenhuma restrição encontrada.")
            
            # Obtém os triggers
            cur.execute("""
                SELECT trigger_name, event_manipulation, action_statement
                FROM information_schema.triggers
                WHERE event_object_table = %s;
            """, (table,))
            
            triggers = cur.fetchall()
            
            if triggers:
                print("\n⚡ Triggers:")
                for trigger in triggers:
                    name, event, action = trigger
                    print(f"- {name} (ON {event}): {action[:100]}...")
            
            # Obtém as regras
            cur.execute("""
                SELECT rulename, definition 
                FROM pg_rules 
                WHERE schemaname = 'public' 
                AND tablename = %s;
            """, (table,))
            
            rules = cur.fetchall()
            
            if rules:
                print("\n📜 Regras:")
                for rule in rules:
                    name, definition = rule
                    print(f"- {name}: {definition[:100]}...")
            
            # Obtém as permissões
            cur.execute("""
                SELECT grantee, privilege_type
                FROM information_schema.role_table_grants
                WHERE table_name = %s
                AND grantee != 'postgres';
            """, (table,))
            
            permissions = cur.fetchall()
            
            if permissions:
                print("\n🔒 Permissões:")
                for perm in permissions:
                    user, priv = perm
                    print(f"- {user}: {priv}")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False
    except psycopg2.Error as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    get_table_constraints()
