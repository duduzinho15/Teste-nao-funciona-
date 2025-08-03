import sqlite3
conn = sqlite3.connect("aposta.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM jogos_historicos")
print("Total de jogos históricos:", cursor.fetchone()[0])
conn.close()