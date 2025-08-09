import sys
import os

print("📂 Diretório atual:", os.getcwd())
print("📦 Conteúdo do diretório:")
for item in os.listdir():
    print(f" - {item}")

print("\n🔍 Tentando importar o módulo...")
try:
    sys.path.append(os.getcwd())  # Adiciona o diretório atual ao PATH
    from database.config import db_manager
    print("✅ Importação bem-sucedida!")
    db_manager.test_connection()
except Exception as e:
    print(f"❌ Erro ao importar: {e}")
    print("\n📌 Dica: Você está executando o script a partir do diretório correto?")