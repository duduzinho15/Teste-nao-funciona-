#!/usr/bin/env python3
"""
Script para criar tabelas de análise de sentimento
=================================================

Este script cria as tabelas necessárias para análise de sentimento
de notícias e posts de redes sociais.

Autor: Sistema de Análise de Sentimento ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

import sqlite3
import os
from datetime import datetime

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

def create_sentiment_tables():
    """Cria as tabelas necessárias para análise de sentimento."""
    db_path = get_db_path()
    
    if not db_path:
        print("❌ Nenhum banco de dados encontrado!")
        return False
    
    print(f"🔍 Conectando ao banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se as tabelas já existem
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tabelas existentes: {existing_tables}")
        
        # Criar tabela noticias_clubes se não existir
        if 'noticias_clubes' not in existing_tables:
            print("🔧 Criando tabela 'noticias_clubes'...")
            cursor.execute("""
                CREATE TABLE noticias_clubes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    clube_id INTEGER NOT NULL,
                    titulo TEXT NOT NULL,
                    url_noticia TEXT UNIQUE NOT NULL,
                    fonte TEXT NOT NULL,
                    data_publicacao DATETIME NOT NULL,
                    resumo TEXT,
                    conteudo_completo TEXT,
                    autor TEXT,
                    imagem_destaque TEXT,
                    
                    -- Campos de sentimento existentes
                    sentimento_geral REAL,
                    confianca_sentimento REAL,
                    polaridade TEXT,
                    
                    -- Campos adicionais para compatibilidade
                    sentimento TEXT,
                    score_sentimento REAL,
                    
                    -- Tópicos e palavras-chave
                    topicos TEXT,
                    palavras_chave TEXT,
                    
                    -- Metadados da análise
                    analisado_em DATETIME,
                    modelo_analise TEXT,
                    
                    -- Timestamps
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (clube_id) REFERENCES clubes (id)
                )
            """)
            print("✅ Tabela 'noticias_clubes' criada com sucesso!")
        else:
            print("ℹ️ Tabela 'noticias_clubes' já existe")
        
        # Criar tabela posts_redes_sociais se não existir
        if 'posts_redes_sociais' not in existing_tables:
            print("🔧 Criando tabela 'posts_redes_sociais'...")
            cursor.execute("""
                CREATE TABLE posts_redes_sociais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    
                    -- Chaves estrangeiras
                    clube_id INTEGER,
                    jogador_id INTEGER,
                    
                    -- Dados do post
                    rede_social TEXT NOT NULL,
                    post_id TEXT NOT NULL,
                    conteudo TEXT,
                    url_post TEXT,
                    data_postagem DATETIME,
                    
                    -- Métricas de engajamento
                    curtidas INTEGER DEFAULT 0,
                    comentarios INTEGER DEFAULT 0,
                    compartilhamentos INTEGER DEFAULT 0,
                    visualizacoes INTEGER DEFAULT 0,
                    
                    -- Metadados
                    tipo_conteudo TEXT,
                    url_imagem TEXT,
                    url_video TEXT,
                    
                    -- Campos de sentimento
                    sentimento TEXT,
                    score_sentimento REAL,
                    
                    -- Timestamps
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Constraints
                    FOREIGN KEY (clube_id) REFERENCES clubes (id),
                    FOREIGN KEY (jogador_id) REFERENCES jogadores (id),
                    UNIQUE(rede_social, post_id),
                    CHECK (clube_id IS NOT NULL OR jogador_id IS NOT NULL)
                )
            """)
            print("✅ Tabela 'posts_redes_sociais' criada com sucesso!")
        else:
            print("ℹ️ Tabela 'posts_redes_sociais' já existe")
        
        # Criar índices para melhorar performance
        print("🔧 Criando índices...")
        
        # Índices para noticias_clubes
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_clube ON noticias_clubes(clube_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_data ON noticias_clubes(data_publicacao)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_fonte ON noticias_clubes(fonte)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_sentimento ON noticias_clubes(sentimento_geral)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_polaridade ON noticias_clubes(polaridade)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_sentimento_new ON noticias_clubes(sentimento)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_noticias_score ON noticias_clubes(score_sentimento)")
            print("✅ Índices para 'noticias_clubes' criados")
        except Exception as e:
            print(f"⚠️ Erro ao criar índices para noticias_clubes: {e}")
        
        # Índices para posts_redes_sociais
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_clube ON posts_redes_sociais(clube_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_jogador ON posts_redes_sociais(jogador_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_rede ON posts_redes_sociais(rede_social)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_data ON posts_redes_sociais(data_postagem)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_sentimento ON posts_redes_sociais(sentimento)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_score ON posts_redes_sociais(score_sentimento)")
            print("✅ Índices para 'posts_redes_sociais' criados")
        except Exception as e:
            print(f"⚠️ Erro ao criar índices para posts_redes_sociais: {e}")
        
        # Verificar a estrutura das tabelas criadas
        print("\n📊 Estrutura das tabelas criadas:")
        
        cursor.execute("PRAGMA table_info(noticias_clubes)")
        columns = cursor.fetchall()
        print(f"\n📋 Tabela 'noticias_clubes':")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute("PRAGMA table_info(posts_redes_sociais)")
        columns = cursor.fetchall()
        print(f"\n📋 Tabela 'posts_redes_sociais':")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.commit()
        print("\n✅ Tabelas criadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Função principal."""
    print("🚀 Iniciando criação de tabelas de análise de sentimento...")
    print("=" * 60)
    
    success = create_sentiment_tables()
    
    print("=" * 60)
    if success:
        print("🎉 Processo concluído com sucesso!")
        print("💡 As tabelas de análise de sentimento foram criadas.")
        print("🔧 Agora você pode executar o script de análise de sentimento.")
    else:
        print("❌ Processo falhou. Verifique os erros acima.")
    
    return success

if __name__ == "__main__":
    main()
