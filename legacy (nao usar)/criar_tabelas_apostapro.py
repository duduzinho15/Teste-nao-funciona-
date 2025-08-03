import sqlite3

# Conectar ao banco
conn = sqlite3.connect('aposta.db')
cursor = conn.cursor()

# Tabela: Estatísticas por jogo
cursor.execute('''
CREATE TABLE IF NOT EXISTS estatisticas_jogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jogo_id INTEGER,
    time TEXT,
    posse REAL,
    escanteios_total INTEGER,
    escanteios_1t INTEGER,
    escanteios_2t INTEGER,
    chutes_total INTEGER,
    chutes_gol INTEGER,
    finalizacoes_bloqueadas INTEGER,
    impedimentos INTEGER,
    faltas INTEGER,
    defesas_goleiro INTEGER,
    passes_completos INTEGER,
    passes_total INTEGER,
    cartões_amarelos INTEGER,
    cartões_vermelhos INTEGER
)
''')

# Tabela: Estatísticas por jogador
cursor.execute('''
CREATE TABLE IF NOT EXISTS estatisticas_jogador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jogo_id INTEGER,
    nome TEXT,
    time TEXT,
    minutos INTEGER,
    gols INTEGER,
    assistencias INTEGER,
    finalizacoes INTEGER,
    finalizacoes_gol INTEGER,
    desarmes INTEGER,
    faltas_cometidas INTEGER,
    cartões_amarelos INTEGER,
    cartões_vermelhos INTEGER,
    defesas_goleiro INTEGER
)
''')

# Tabela: Odds e mercados avançados
cursor.execute('''
CREATE TABLE IF NOT EXISTS odds_mercados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jogo_id INTEGER,
    mercado TEXT,
    selecao TEXT,
    odd REAL
)
''')

# Tabela: Palpites gerados pela IA
cursor.execute('''
CREATE TABLE IF NOT EXISTS palpites_ia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jogo_id INTEGER,
    mercado TEXT,
    palpite TEXT,
    probabilidade REAL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("✅ Tabelas criadas com sucesso no banco 'aposta.db'")
