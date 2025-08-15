# health_check_db.py
from Coleta_de_dados.database.config import SessionLocal
from sqlalchemy import text

print("Verificando conexão com o banco de dados...")
try:
    db = SessionLocal()
    result = db.execute(text("SELECT 1"))
    print("✅ Conexão com o banco de dados bem-sucedida.")
    print(f"Resultado do teste: {result.scalar()}")
    db.close()
except Exception as e:
    print(f"❌ Falha na conexão com o banco de dados: {e}")
    raise
