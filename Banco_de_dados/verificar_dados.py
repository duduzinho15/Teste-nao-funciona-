import sqlite3
import os

# Caminho do banco
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Banco_de_dados', 'aposta.db')

# Lista de tabelas para checar
TABELAS = [
    'ligas',
    'times',
    'jogadores',
    'jogos_historicos',
    'jogos_futuros',
    'estatisticas',
    'estatisticas_partidas',
    'palpites',
    'perfis',
    'notificacoes',
    'sofascore_temp',
    'thesportsdb'
]

def verificar_dados():
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return

    print("\n📊 VERIFICAÇÃO DE DADOS DO BANCO 'aposta.db':\n")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for tabela in TABELAS:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                total = cursor.fetchone()[0]
                print(f"✅ {tabela}: {total} registro(s)")
            except sqlite3.OperationalError as e:
                print(f"❌ {tabela}: ERRO - {e}")

if __name__ == "__main__":
    verificar_dados()
