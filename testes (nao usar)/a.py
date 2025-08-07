import sqlite3

DB_PATH = "Banco_de_dados/aposta.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(fbref_com_temp)")
colunas = cursor.fetchall()
conn.close()

print("📋 Colunas da tabela fbref_com_temp:")
for col in colunas:
    print(f"- {col[1]} ({col[2]})")
