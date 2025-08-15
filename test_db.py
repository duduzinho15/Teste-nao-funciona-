"""
Script para testar a conexão com o banco de dados e criar as tabelas necessárias.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def test_connection():
    # String de conexão usando as credenciais do .env
    conn_str = "postgresql://apostapro_user:senha_segura_123@localhost:5432/apostapro_db"
    
    try:
        print("🔍 Testando conexão com o banco de dados...")
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            # Testa a conexão
            result = conn.execute(text("SELECT 'Conexão bem-sucedida!' AS message"))
            print(f"✅ {result.scalar()}")
            
            # Verifica se a tabela de partidas existe
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'partidas')"
            ))
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ Tabela 'partidas' encontrada.")
                # Conta o número de partidas
                result = conn.execute(text("SELECT COUNT(*) FROM partidas"))
                count = result.scalar()
                print(f"ℹ️  Número de partidas no banco: {count}")
            else:
                print("⚠️  Tabela 'partidas' não encontrada.")
                
        return True
        
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🔧 Iniciando teste de conexão com o banco de dados...")
    success = test_connection()
    
    if not success:
        print("\n📌 Possíveis soluções:")
        print("1. Verifique se o PostgreSQL está rodando")
        print("2. Confirme as credenciais no arquivo .env")
        print("3. Verifique se o banco de dados 'apostapro_db' existe")
        print("4. Verifique se o usuário 'apostapro_user' tem permissões adequadas")
        print("\n🔧 Tente executar o script de inicialização do banco de dados primeiro:")
        print("   python init_db.py")
        sys.exit(1)
    else:
        print("\n✅ Teste de conexão concluído com sucesso!")
