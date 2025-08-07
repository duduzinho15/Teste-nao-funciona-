import sys
import os

# Adiciona o diretório Coleta_de_dados ao PATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'Coleta_de_dados'))

try:
    from database.config import db_manager
    print("✅ Módulo importado com sucesso!")
    
    # Testar conexão
    print("\n🔍 Testando conexão com o banco de dados...")
    if db_manager.test_connection():
        print("✅ Conexão bem-sucedida!")
        print(f"📊 Status do pool: {db_manager.get_pool_status()}")
    else:
        print("❌ Falha na conexão com o banco de dados")
        
except Exception as e:
    print(f"❌ Erro ao importar ou conectar: {e}")
    print("\n📌 Verifique se o arquivo .env está configurado corretamente")