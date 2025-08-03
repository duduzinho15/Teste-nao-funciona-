#!/usr/bin/env python3
"""
Script para verificar as tabelas corretas do sistema FBRef.
"""

import sqlite3
import os

# Caminho do banco
DB_PATH = os.path.join('Banco_de_dados', 'aposta.db')

def verificar_tabelas_fbref():
    """Verifica as tabelas do sistema FBRef."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return

    print("\n📊 VERIFICAÇÃO DE TABELAS FBREF NO BANCO 'aposta.db':\n")
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Lista todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print(f"📋 Total de tabelas encontradas: {len(tabelas)}")
        print("\n📊 TABELAS DISPONÍVEIS:")
        
        for tabela in tabelas:
            nome_tabela = tabela[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
                total = cursor.fetchone()[0]
                print(f"✅ {nome_tabela}: {total} registro(s)")
            except sqlite3.OperationalError as e:
                print(f"❌ {nome_tabela}: ERRO - {e}")
        
        # Verifica tabelas específicas do FBRef
        tabelas_fbref = [
            'competicoes',
            'links_para_coleta',
            'partidas',
            'estatisticas_partidas',
            'paises_clubes',
            'clubes',
            'estatisticas_clube',
            'records_vs_opponents',
            'paises_jogadores',
            'jogadores',
            'estatisticas_jogador_geral',
            'estatisticas_jogador_competicao'
        ]
        
        print(f"\n🎯 TABELAS ESPECÍFICAS DO FBREF:")
        for tabela in tabelas_fbref:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                total = cursor.fetchone()[0]
                print(f"✅ {tabela}: {total} registro(s)")
            except sqlite3.OperationalError:
                print(f"❌ {tabela}: Tabela não existe")

if __name__ == "__main__":
    verificar_tabelas_fbref() 