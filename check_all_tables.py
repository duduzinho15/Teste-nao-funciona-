"""
Script para listar todas as tabelas no banco de dados e suas estruturas.
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def list_all_tables():
    # String de conexão
    conn_str = "postgresql://apostapro_user:senha_segura_123@localhost:5432/apostapro_db"
    
    try:
        print("🔍 Conectando ao banco de dados...")
        engine = create_engine(conn_str)
        
        with engine.connect() as conn:
            # Lista todas as tabelas
            print("\n📋 Tabelas disponíveis no banco de dados:")
            print("=" * 50)
            
            # Obtém a lista de tabelas
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            table_count = 0
            all_tables = []
            
            for table in tables:
                table_name = table[0]
                all_tables.append(table_name)
                table_count += 1
                
                # Conta os registros na tabela
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = count_result.scalar()
                    print(f"- {table_name} ({count} registros)")
                except:
                    print(f"- {table_name} (erro ao contar registros)")
            
            print(f"\n✅ Total de tabelas encontradas: {table_count}")
            
            # Se não houver tabelas, sugere executar o script de inicialização
            if table_count == 0:
                print("\n❌ Nenhuma tabela encontrada no banco de dados.")
                print("   Execute o script de inicialização do banco de dados (init_db.py) para criar as tabelas.")
            
            return 0, all_tables
            
    except SQLAlchemyError as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
        return 1, []
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1, []
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🔍 Listando todas as tabelas do banco de dados...")
    sys.exit(list_all_tables()[0])
