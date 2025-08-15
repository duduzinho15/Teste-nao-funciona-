"""
Script para verificar a estrutura e os dados da tabela 'clubes'.
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def check_clubes_table():
    # String de conexão
    conn_str = "postgresql://apostapro_user:senha_segura_123@localhost:5432/apostapro_db"
    
    try:
        print("🔍 Conectando ao banco de dados...")
        engine = create_engine(conn_str)
        
        with engine.connect() as conn:
            # Verifica se a tabela 'clubes' existe
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'clubes')"
            ))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ A tabela 'clubes' não existe no banco de dados.")
                return 1
            
            print("✅ Tabela 'clubes' encontrada.")
            
            # Obtém a estrutura da tabela
            print("\n📋 Estrutura da tabela 'clubes':")
            print("=" * 50)
            
            columns = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'clubes'
                ORDER BY ordinal_position
            """))
            
            for col in columns:
                print(f"- {col[0]}: {col[1]} (nullable: {col[2]}){' DEFAULT: ' + str(col[3]) if col[3] else ''}")
            
            # Conta os registros
            result = conn.execute(text("SELECT COUNT(*) FROM clubes"))
            count = result.scalar()
            print(f"\n📊 Total de clubes cadastrados: {count}")
            
            # Mostra os primeiros 5 clubes, se houver
            if count > 0:
                print("\n🏆 Primeiros clubes cadastrados:")
                clubes = conn.execute(text("SELECT id, nome, abreviacao, pais_id, url_escudo FROM clubes LIMIT 5"))
                for clube in clubes:
                    print(f"- ID: {clube[0]}, Nome: {clube[1]}, Abreviação: {clube[2] or 'N/A'}, País ID: {clube[3]}, Escudo: {clube[4] or 'N/A'}")
            
            return 0
            
    except SQLAlchemyError as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
        return 1
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🔍 Verificando a tabela 'clubes'...")
    sys.exit(check_clubes_table())
