import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

def testar_conexao():
    # URL de conexão idêntica à usada pelo Alembic
    db_url = "postgresql://apostapro_user:Canjica@@2025@localhost:5432/apostapro_db?host=localhost"
    
    print(f"🔍 Testando conexão com: {db_url}")
    
    try:
        # Criar engine com configurações semelhantes ao Alembic
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,
            max_overflow=10
        )
        
        # Testar conexão
        with engine.connect() as connection:
            print("✅ Conexão bem-sucedida!")
            
            # Obter informações do banco de dados
            result = connection.execute("SELECT version(), current_database(), current_user")
            version, db_name, db_user = result.fetchone()
            
            print(f"📊 Informações do servidor:")
            print(f" - PostgreSQL: {version}")
            print(f" - Banco de dados: {db_name}")
            print(f" - Usuário: {db_user}")
            
            # Verificar se o banco de dados está vazio
            result = connection.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
            tabelas = [row[0] for row in result]
            
            if tabelas:
                print(f"\n📋 Tabelas encontradas ({len(tabelas)}):")
                for tabela in sorted(tabelas):
                    print(f" - {tabela}")
            else:
                print("\nℹ️  Nenhuma tabela encontrada no banco de dados.")
        
        return True
        
    except OperationalError as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    testar_conexao()
    input("\nPressione Enter para sair...")
