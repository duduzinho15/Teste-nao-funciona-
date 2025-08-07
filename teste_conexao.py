import sys
import os

# Adiciona o diretório raiz ao caminho de importação
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.config import db_manager

def testar_conexao():
    print("🔍 Testando conexão com o banco de dados...")
    print(f"📊 Banco: {db_manager.settings.db_name}")
    print(f"👤 Usuário: {db_manager.settings.db_user}")
    
    if db_manager.test_connection():
        print("✅ Conexão bem-sucedida!")
        print(f"📊 Status do pool: {db_manager.get_pool_status()}")
    else:
        print("❌ Falha na conexão com o banco de dados")

if __name__ == "__main__":
    testar_conexao()