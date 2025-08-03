import sqlite3

conn = sqlite3.connect('aposta.db')
cursor = conn.cursor()

# Verifica estrutura da tabela
cursor.execute("PRAGMA table_info(jogos_historicos)")
colunas = cursor.fetchall()

print("🔎 Colunas disponíveis na tabela 'jogos_historicos':\n")
for coluna in colunas:
    print(f"- {coluna[1]}")
    
conn.close()
