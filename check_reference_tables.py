"""
Script para verificar as tabelas de referência necessárias para a tabela 'partidas'.
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def check_reference_tables():
    # String de conexão
    conn_str = "postgresql://apostapro_user:senha_segura_123@localhost:5432/apostapro_db"
    
    try:
        print("🔍 Conectando ao banco de dados...")
        engine = create_engine(conn_str)
        
        with engine.connect() as conn:
            # Tabelas de referência necessárias
            reference_tables = [
                'clubes',
                'competicoes',
                'estadios'
            ]
            
            all_tables_exist = True
            
            # Verifica cada tabela de referência
            for table in reference_tables:
                result = conn.execute(text(
                    f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"
                ))
                table_exists = result.scalar()
                
                if not table_exists:
                    print(f"❌ A tabela '{table}' não existe no banco de dados.")
                    all_tables_exist = False
                else:
                    # Conta os registros na tabela
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.scalar()
                    print(f"✅ Tabela '{table}' encontrada com {count} registros.")
            
            if not all_tables_exist:
                print("\n❌ Algumas tabelas de referência não existem.")
                return 1
            
            # Verifica se há pelo menos 2 clubes, 1 competição e 1 estádio
            min_requirements = {
                'clubes': 2,
                'competicoes': 1,
                'estadios': 1
            }
            
            requirements_met = True
            
            for table, min_count in min_requirements.items():
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                
                if count < min_count:
                    print(f"❌ A tabela '{table}' tem apenas {count} registro(s). Mínimo necessário: {min_count}")
                    requirements_met = False
                else:
                    print(f"✅ A tabela '{table}' tem {count} registro(s). Atende ao mínimo de {min_count}.")
            
            if not requirements_met:
                print("\n❌ Algumas tabelas não atendem aos requisitos mínimos de registros.")
                return 1
            
            print("\n✅ Todas as tabelas de referência existem e atendem aos requisitos mínimos de registros.")
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
    print("🔍 Verificando tabelas de referência necessárias para a tabela 'partidas'...")
    sys.exit(check_reference_tables())
