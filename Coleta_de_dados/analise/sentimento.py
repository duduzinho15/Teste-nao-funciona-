#!/usr/bin/env python3
"""
Script de Análise de Sentimento para Notícias e Posts
=====================================================

Este script analisa o sentimento de notícias e posts de redes sociais
usando a biblioteca TextBlob para NLP.

Autor: Sistema de Análise de Sentimento ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

import sqlite3
import os
from datetime import datetime
from textblob import TextBlob
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

def analisar_sentimento_texto(texto):
    """
    Analisa o sentimento de um texto usando TextBlob.
    
    Args:
        texto (str): Texto para análise
        
    Returns:
        tuple: (sentimento, score_sentimento, confianca)
    """
    if not texto or not texto.strip():
        return 'neutro', 0.0, 0.0
    
    try:
        # Criar objeto TextBlob para análise
        blob = TextBlob(texto)
        
        # Obter polaridade (-1 a 1) e subjetividade (0 a 1)
        polaridade = blob.sentiment.polarity
        subjetividade = blob.sentiment.subjectivity
        
        # Classificar sentimento baseado na polaridade
        if polaridade > 0.1:
            sentimento = 'positivo'
        elif polaridade < -0.1:
            sentimento = 'negativo'
        else:
            sentimento = 'neutro'
        
        # Calcular confiança baseada na subjetividade
        # Quanto mais subjetivo, menos confiável é a análise
        confianca = 1.0 - subjetividade
        
        return sentimento, polaridade, confianca
        
    except Exception as e:
        logger.error(f"Erro ao analisar sentimento do texto: {e}")
        return 'neutro', 0.0, 0.0

def analisar_sentimento_textos():
    """
    Busca por notícias e posts sem análise de sentimento, calcula o sentimento
    usando TextBlob e atualiza os registros no banco de dados.
    """
    db_path = get_db_path()
    
    if not db_path:
        logger.error("Nenhum banco de dados encontrado!")
        return False
    
    print("🚀 Iniciando análise de sentimento de textos pendentes...")
    print(f"🔍 Conectando ao banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar notícias sem análise de sentimento
        cursor.execute("""
            SELECT id, titulo, resumo, conteudo_completo 
            FROM noticias_clubes 
            WHERE sentimento IS NULL OR score_sentimento IS NULL
        """)
        noticias_pendentes = cursor.fetchall()
        
        # Buscar posts sem análise de sentimento
        cursor.execute("""
            SELECT id, conteudo 
            FROM posts_redes_sociais 
            WHERE sentimento IS NULL OR score_sentimento IS NULL
        """)
        posts_pendentes = cursor.fetchall()
        
        total_itens = len(noticias_pendentes) + len(posts_pendentes)
        
        if total_itens == 0:
            print("✅ Nenhum item novo para analisar.")
            return True
        
        print(f"📊 Encontrados {len(noticias_pendentes)} notícias e {len(posts_pendentes)} posts para análise")
        
        # Processar notícias
        noticias_processadas = 0
        for noticia_id, titulo, resumo, conteudo_completo in noticias_pendentes:
            try:
                # Combinar título, resumo e conteúdo para análise
                texto_completo = f"{titulo or ''} {resumo or ''} {conteudo_completo or ''}".strip()
                
                if not texto_completo:
                    continue
                
                # Analisar sentimento
                sentimento, score, confianca = analisar_sentimento_texto(texto_completo)
                
                # Atualizar banco de dados
                cursor.execute("""
                    UPDATE noticias_clubes 
                    SET sentimento = ?, score_sentimento = ?, 
                        sentimento_geral = ?, confianca_sentimento = ?,
                        polaridade = ?, analisado_em = ?, modelo_analise = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (sentimento, score, score, confianca, sentimento, datetime.now(), 'TextBlob', noticia_id))
                
                noticias_processadas += 1
                
                if noticias_processadas % 10 == 0:
                    print(f"📰 Processadas {noticias_processadas} notícias...")
                    
            except Exception as e:
                logger.error(f"Erro ao processar notícia {noticia_id}: {e}")
                continue
        
        # Processar posts
        posts_processados = 0
        for post_id, conteudo in posts_pendentes:
            try:
                if not conteudo or not conteudo.strip():
                    continue
                
                # Analisar sentimento
                sentimento, score, confianca = analisar_sentimento_texto(conteudo)
                
                # Atualizar banco de dados
                cursor.execute("""
                    UPDATE posts_redes_sociais 
                    SET sentimento = ?, score_sentimento = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (sentimento, score, post_id))
                
                posts_processados += 1
                
                if posts_processados % 10 == 0:
                    print(f"📱 Processados {posts_processados} posts...")
                    
            except Exception as e:
                logger.error(f"Erro ao processar post {post_id}: {e}")
                continue
        
        # Commit das alterações
        conn.commit()
        
        print(f"\n✅ Análise de sentimento concluída!")
        print(f"📊 Resumo:")
        print(f"   - Notícias processadas: {noticias_processadas}")
        print(f"   - Posts processados: {posts_processados}")
        print(f"   - Total: {noticias_processadas + posts_processados}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante análise de sentimento: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def obter_estatisticas_sentimento():
    """
    Obtém estatísticas sobre a análise de sentimento realizada.
    
    Returns:
        dict: Estatísticas de sentimento
    """
    db_path = get_db_path()
    
    if not db_path:
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Estatísticas de notícias
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN sentimento = 'positivo' THEN 1 END) as positivas,
                COUNT(CASE WHEN sentimento = 'negativo' THEN 1 END) as negativas,
                COUNT(CASE WHEN sentimento = 'neutro' THEN 1 END) as neutras,
                AVG(score_sentimento) as score_medio
            FROM noticias_clubes 
            WHERE sentimento IS NOT NULL
        """)
        stats_noticias = cursor.fetchone()
        
        # Estatísticas de posts
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN sentimento = 'positivo' THEN 1 END) as positivos,
                COUNT(CASE WHEN sentimento = 'negativo' THEN 1 END) as negativos,
                COUNT(CASE WHEN sentimento = 'neutro' THEN 1 END) as neutros,
                AVG(score_sentimento) as score_medio
            FROM posts_redes_sociais 
            WHERE sentimento IS NOT NULL
        """)
        stats_posts = cursor.fetchone()
        
        # Sentimento por clube (top 5)
        cursor.execute("""
            SELECT 
                c.nome as clube,
                COUNT(n.id) as total_noticias,
                AVG(n.score_sentimento) as score_medio,
                COUNT(CASE WHEN n.sentimento = 'positivo' THEN 1 END) as positivas,
                COUNT(CASE WHEN n.sentimento = 'negativo' THEN 1 END) as negativas
            FROM noticias_clubes n
            JOIN clubes c ON n.clube_id = c.id
            WHERE n.sentimento IS NOT NULL
            GROUP BY c.id, c.nome
            ORDER BY total_noticias DESC
            LIMIT 5
        """)
        top_clubes = cursor.fetchall()
        
        return {
            'noticias': {
                'total': stats_noticias[0] or 0,
                'positivas': stats_noticias[1] or 0,
                'negativas': stats_noticias[2] or 0,
                'neutras': stats_noticias[3] or 0,
                'score_medio': stats_noticias[4] or 0.0
            },
            'posts': {
                'total': stats_posts[0] or 0,
                'positivos': stats_posts[1] or 0,
                'negativos': stats_posts[2] or 0,
                'neutros': stats_posts[3] or 0,
                'score_medio': stats_posts[4] or 0.0
            },
            'top_clubes': [
                {
                    'nome': clube[0],
                    'total_noticias': clube[1],
                    'score_medio': clube[2] or 0.0,
                    'positivas': clube[3],
                    'negativas': clube[4]
                }
                for clube in top_clubes
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return None
    
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Função principal."""
    print("🧠 Sistema de Análise de Sentimento ApostaPro")
    print("=" * 50)
    
    # Executar análise de sentimento
    success = analisar_sentimento_textos()
    
    if success:
        print("\n📊 Obtendo estatísticas...")
        stats = obter_estatisticas_sentimento()
        
        if stats:
            print("\n📈 Estatísticas de Sentimento:")
            print(f"📰 Notícias:")
            print(f"   - Total: {stats['noticias']['total']}")
            print(f"   - Positivas: {stats['noticias']['positivas']}")
            print(f"   - Negativas: {stats['noticias']['negativas']}")
            print(f"   - Neutras: {stats['noticias']['neutras']}")
            print(f"   - Score médio: {stats['noticias']['score_medio']:.3f}")
            
            print(f"\n📱 Posts:")
            print(f"   - Total: {stats['posts']['total']}")
            print(f"   - Positivos: {stats['posts']['positivos']}")
            print(f"   - Negativos: {stats['posts']['negativos']}")
            print(f"   - Neutros: {stats['posts']['neutros']}")
            print(f"   - Score médio: {stats['posts']['score_medio']:.3f}")
            
            if stats['top_clubes']:
                print(f"\n🏆 Top 5 Clubes por Notícias:")
                for i, clube in enumerate(stats['top_clubes'], 1):
                    print(f"   {i}. {clube['nome']}: {clube['total_noticias']} notícias (score: {clube['score_medio']:.3f})")
        
        print("\n🎉 Análise de sentimento concluída com sucesso!")
    else:
        print("\n❌ Falha na análise de sentimento.")
    
    return success

if __name__ == '__main__':
    main()
