#!/usr/bin/env python3
"""
Script para adicionar colunas de análise de sentimento ao banco de dados
======================================================================

Este script adiciona as colunas necessárias para análise de sentimento
nas tabelas de notícias e posts de redes sociais.

Autor: Sistema de Análise de Sentimento ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

import sqlite3
import os
from pathlib import Path

def get_db_path():
    """Obtém o caminho para o banco de dados."""
    # Tentar diferentes localizações possíveis
    possible_paths = [
        "Banco_de_dados/aposta.db",
        "Coleta_de_dados/database/football_data.db",
        "aposta.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def add_sentiment_columns():
    """Adiciona colunas de sentimento às tabelas necessárias."""
    db_path = get_db_path()
    
    if not db_path:
        print("❌ Nenhum banco de dados encontrado!")
        return False
    
    print(f"🔍 Conectando ao banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se as tabelas existem
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tabelas encontradas: {tables}")
        
        # Adicionar colunas à tabela noticias_clubes (se existir)
        if 'noticias_clubes' in tables:
            print("🔧 Adicionando colunas de sentimento à tabela noticias_clubes...")
            try:
                cursor.execute("""
                    ALTER TABLE noticias_clubes 
                    ADD COLUMN sentimento TEXT DEFAULT NULL
                """)
                print("✅ Coluna 'sentimento' adicionada com sucesso!")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("ℹ️ Coluna 'sentimento' já existe")
                else:
                    print(f"⚠️ Erro ao adicionar coluna 'sentimento': {e}")
            
            try:
                cursor.execute("""
                    ALTER TABLE noticias_clubes 
                    ADD COLUMN score_sentimento REAL DEFAULT NULL
                """)
                print("✅ Coluna 'score_sentimento' adicionada com sucesso!")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("ℹ️ Coluna 'score_sentimento' já existe")
                else:
                    print(f"⚠️ Erro ao adicionar coluna 'score_sentimento': {e}")
        else:
            print("⚠️ Tabela 'noticias_clubes' não encontrada")
        
        # Adicionar colunas à tabela posts_redes_sociais (se existir)
        if 'posts_redes_sociais' in tables:
            print("🔧 Adicionando colunas de sentimento à tabela posts_redes_sociais...")
            try:
                cursor.execute("""
                    ALTER TABLE posts_redes_sociais 
                    ADD COLUMN sentimento TEXT DEFAULT NULL
                """)
                print("✅ Coluna 'sentimento' adicionada com sucesso!")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("ℹ️ Coluna 'sentimento' já existe")
                else:
                    print(f"⚠️ Erro ao adicionar coluna 'sentimento': {e}")
            
            try:
                cursor.execute("""
                    ALTER TABLE posts_redes_sociais 
                    ADD COLUMN score_sentimento REAL DEFAULT NULL
                """)
                print("✅ Coluna 'score_sentimento' adicionada com sucesso!")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("ℹ️ Coluna 'score_sentimento' já existe")
                else:
                    print(f"⚠️ Erro ao adicionar coluna 'score_sentimento': {e}")
        else:
            print("⚠️ Tabela 'posts_redes_sociais' não encontrada")
        
        # Verificar a estrutura das tabelas após as modificações
        print("\n📊 Estrutura das tabelas após modificações:")
        
        if 'noticias_clubes' in tables:
            cursor.execute("PRAGMA table_info(noticias_clubes)")
            columns = cursor.fetchall()
            print(f"\n📋 Tabela 'noticias_clubes':")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        if 'posts_redes_sociais' in tables:
            cursor.execute("PRAGMA table_info(posts_redes_sociais)")
            columns = cursor.fetchall()
            print(f"\n📋 Tabela 'posts_redes_sociais':")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        conn.commit()
        print("\n✅ Modificações aplicadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao modificar banco de dados: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Função principal."""
    print("🚀 Iniciando adição de colunas de análise de sentimento...")
    print("=" * 60)
    
    success = add_sentiment_columns()
    
    print("=" * 60)
    if success:
        print("🎉 Processo concluído com sucesso!")
        print("💡 As colunas de sentimento foram adicionadas ao banco de dados.")
        print("🔧 Agora você pode executar o script de análise de sentimento.")
    else:
        print("❌ Processo falhou. Verifique os erros acima.")
    
    return success

if __name__ == "__main__":
    main()
