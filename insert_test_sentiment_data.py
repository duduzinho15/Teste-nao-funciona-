#!/usr/bin/env python3
"""
Script para inserir dados de teste para análise de sentimento
============================================================

Este script insere notícias e posts de teste no banco de dados
para permitir a validação da análise de sentimento.

Autor: Sistema de Análise de Sentimento ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def get_db_path():
    """Obtém o caminho para o banco de dados."""
    possible_paths = [
        "Banco_de_dados/aposta.db",
        "Coleta_de_dados/database/football_data.db",
        "aposta.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def insert_test_data():
    """Insere dados de teste para análise de sentimento."""
    db_path = get_db_path()
    
    if not db_path:
        print("❌ Nenhum banco de dados encontrado!")
        return False
    
    print(f"🔍 Conectando ao banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se existem clubes
        cursor.execute("SELECT id, nome FROM clubes LIMIT 5")
        clubes = cursor.fetchall()
        
        if not clubes:
            print("⚠️ Nenhum clube encontrado. Criando clubes de teste...")
            
            # Criar clubes de teste
            clubes_teste = [
                (1, "Flamengo", 1, "M", "https://fbref.com/teams/598bc722/Flamengo", "https://fbref.com/teams/598bc722/Flamengo", "ativo", "ativo"),
                (2, "Palmeiras", 1, "M", "https://fbref.com/teams/1963d509/Palmeiras", "https://fbref.com/teams/1963d509/Palmeiras", "ativo", "ativo"),
                (3, "Santos", 1, "M", "https://fbref.com/teams/2f1ebc7c/Santos", "https://fbref.com/teams/2f1ebc7c/Santos", "ativo", "ativo"),
                (4, "Corinthians", 1, "M", "https://fbref.com/teams/19538871/Corinthians", "https://fbref.com/teams/19538871/Corinthians", "ativo", "ativo"),
                (5, "São Paulo", 1, "M", "https://fbref.com/teams/24c87dd6/Sao-Paulo", "https://fbref.com/teams/24c87dd6/Sao-Paulo", "ativo", "ativo")
            ]
            
            for clube in clubes_teste:
                try:
                    cursor.execute("""
                        INSERT INTO clubes (id, nome, pais_id, genero, url_clube, url_records_vs_opponents, status_coleta, status_records)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, clube)
                except sqlite3.IntegrityError:
                    print(f"ℹ️ Clube {clube[1]} já existe")
            
            clubes = clubes_teste
            print("✅ Clubes de teste criados")
        
        # Dados de teste para notícias
        noticias_teste = [
            # Notícias positivas
            {
                'clube_id': 1,
                'titulo': 'Flamengo vence clássico com atuação espetacular',
                'url_noticia': 'https://exemplo.com/noticia1',
                'fonte': 'Globo Esporte',
                'data_publicacao': datetime.now() - timedelta(days=1),
                'resumo': 'Time rubro-negro domina o jogo e conquista vitória importante',
                'conteudo_completo': 'O Flamengo apresentou uma atuação espetacular no clássico, demonstrando superioridade técnica e tática. Os jogadores mostraram determinação e qualidade, resultando em uma vitória convincente que deixa a torcida muito satisfeita.'
            },
            {
                'clube_id': 2,
                'titulo': 'Palmeiras conquista título com futebol ofensivo',
                'url_noticia': 'https://exemplo.com/noticia2',
                'fonte': 'ESPN',
                'data_publicacao': datetime.now() - timedelta(days=2),
                'resumo': 'Verde conquista campeonato com estilo de jogo envolvente',
                'conteudo_completo': 'O Palmeiras conquistou o título de forma brilhante, apresentando um futebol ofensivo e envolvente. A equipe demonstrou grande qualidade técnica e espírito de equipe, deixando todos os torcedores orgulhosos da conquista.'
            },
            # Notícias negativas
            {
                'clube_id': 3,
                'titulo': 'Santos sofre derrota amarga no campeonato',
                'url_noticia': 'https://exemplo.com/noticia3',
                'fonte': 'UOL Esporte',
                'data_publicacao': datetime.now() - timedelta(days=3),
                'resumo': 'Peixe perde jogo importante e complica situação na tabela',
                'conteudo_completo': 'O Santos sofreu uma derrota amarga que complica ainda mais sua situação no campeonato. A equipe apresentou um futebol abaixo do esperado, com erros defensivos e falta de criatividade no ataque, deixando a torcida frustrada.'
            },
            {
                'clube_id': 4,
                'titulo': 'Corinthians enfrenta crise no elenco',
                'url_noticia': 'https://exemplo.com/noticia4',
                'fonte': 'Band',
                'data_publicacao': datetime.now() - timedelta(days=4),
                'resumo': 'Time alvinegro passa por momento difícil com lesões e suspensões',
                'conteudo_completo': 'O Corinthians enfrenta uma crise séria no elenco, com várias lesões e suspensões importantes. A situação é preocupante e pode comprometer o desempenho da equipe nos próximos jogos, gerando ansiedade na torcida.'
            },
            # Notícias neutras
            {
                'clube_id': 5,
                'titulo': 'São Paulo anuncia novo reforço para o elenco',
                'url_noticia': 'https://exemplo.com/noticia5',
                'fonte': 'Gazeta Esportiva',
                'data_publicacao': datetime.now() - timedelta(days=5),
                'resumo': 'Tricolor contrata jogador para fortalecer o meio-campo',
                'conteudo_completo': 'O São Paulo anunciou a contratação de um novo jogador para fortalecer o meio-campo. A diretoria avalia que o atleta pode contribuir para o projeto da equipe, mas ainda é cedo para avaliar o impacto da contratação.'
            }
        ]
        
        # Inserir notícias de teste
        print("📰 Inserindo notícias de teste...")
        for noticia in noticias_teste:
            try:
                cursor.execute("""
                    INSERT INTO noticias_clubes (
                        clube_id, titulo, url_noticia, fonte, data_publicacao,
                        resumo, conteudo_completo, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    noticia['clube_id'], noticia['titulo'], noticia['url_noticia'],
                    noticia['fonte'], noticia['data_publicacao'], noticia['resumo'],
                    noticia['conteudo_completo']
                ))
                print(f"✅ Notícia inserida: {noticia['titulo'][:30]}...")
            except sqlite3.IntegrityError as e:
                print(f"ℹ️ Notícia já existe: {noticia['titulo'][:30]}...")
        
        # Dados de teste para posts de redes sociais
        posts_teste = [
            # Posts positivos
            {
                'clube_id': 1,
                'rede_social': 'twitter',
                'post_id': 'post1_flamengo',
                'conteudo': 'Que vitória espetacular! 🏆 O time jogou demais hoje! #Flamengo #VamosFlamengo',
                'data_postagem': datetime.now() - timedelta(hours=2),
                'curtidas': 1500,
                'comentarios': 300,
                'compartilhamentos': 200
            },
            {
                'clube_id': 2,
                'rede_social': 'instagram',
                'post_id': 'post1_palmeiras',
                'conteudo': 'Campeões! 🎉 Que orgulho desta equipe! #Palmeiras #Campeao',
                'data_postagem': datetime.now() - timedelta(hours=4),
                'curtidas': 2000,
                'comentarios': 400,
                'compartilhamentos': 300
            },
            # Posts negativos
            {
                'clube_id': 3,
                'rede_social': 'facebook',
                'post_id': 'post1_santos',
                'conteudo': 'Que jogo ruim... 😞 Precisamos melhorar muito! #Santos #VamosMelhorar',
                'data_postagem': datetime.now() - timedelta(hours=6),
                'curtidas': 800,
                'comentarios': 150,
                'compartilhamentos': 50
            },
            {
                'clube_id': 4,
                'rede_social': 'twitter',
                'post_id': 'post1_corinthians',
                'conteudo': 'Situação difícil... 😔 Vamos superar essa crise! #Corinthians #Foco',
                'data_postagem': datetime.now() - timedelta(hours=8),
                'curtidas': 1200,
                'comentarios': 250,
                'compartilhamentos': 100
            },
            # Posts neutros
            {
                'clube_id': 5,
                'rede_social': 'instagram',
                'post_id': 'post1_saopaulo',
                'conteudo': 'Novo reforço anunciado! 🤝 Bem-vindo ao clube! #SaoPaulo #NovoJogador',
                'data_postagem': datetime.now() - timedelta(hours=10),
                'curtidas': 900,
                'comentarios': 180,
                'compartilhamentos': 80
            }
        ]
        
        # Inserir posts de teste
        print("📱 Inserindo posts de teste...")
        for post in posts_teste:
            try:
                cursor.execute("""
                    INSERT INTO posts_redes_sociais (
                        clube_id, rede_social, post_id, conteudo, data_postagem,
                        curtidas, comentarios, compartilhamentos, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    post['clube_id'], post['rede_social'], post['post_id'],
                    post['conteudo'], post['data_postagem'], post['curtidas'],
                    post['comentarios'], post['compartilhamentos']
                ))
                print(f"✅ Post inserido: {post['conteudo'][:30]}...")
            except sqlite3.IntegrityError as e:
                print(f"ℹ️ Post já existe: {post['conteudo'][:30]}...")
        
        # Commit das alterações
        conn.commit()
        
        # Verificar dados inseridos
        cursor.execute("SELECT COUNT(*) FROM noticias_clubes")
        total_noticias = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM posts_redes_sociais")
        total_posts = cursor.fetchone()[0]
        
        print(f"\n📊 Dados de teste inseridos:")
        print(f"   - Notícias: {total_noticias}")
        print(f"   - Posts: {total_posts}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados de teste: {e}")
        return False

def main():
    """Função principal."""
    print("🚀 Inserindo dados de teste para análise de sentimento...")
    print("=" * 60)
    
    success = insert_test_data()
    
    print("=" * 60)
    if success:
        print("🎉 Dados de teste inseridos com sucesso!")
        print("💡 Agora você pode executar o script de análise de sentimento.")
    else:
        print("❌ Falha na inserção de dados de teste.")
    
    return success

if __name__ == "__main__":
    main()
