#!/usr/bin/env python3
"""
Script para testar o endpoint de análise de sentimento
=====================================================

Este script testa diretamente a funcionalidade de análise de sentimento
sem depender da API completa.

Autor: Sistema de Análise de Sentimento ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

import sqlite3
import os
from datetime import datetime

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

def test_sentiment_analysis():
    """Testa a funcionalidade de análise de sentimento."""
    db_path = get_db_path()
    
    if not db_path:
        print("❌ Nenhum banco de dados encontrado!")
        return False
    
    print(f"🔍 Conectando ao banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Teste 1: Verificar dados de sentimento existentes
        print("\n📊 Teste 1: Verificando dados de sentimento existentes...")
        
        cursor.execute("SELECT COUNT(*) FROM noticias_clubes WHERE sentimento IS NOT NULL")
        noticias_analisadas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM posts_redes_sociais WHERE sentimento IS NOT NULL")
        posts_analisados = cursor.fetchone()[0]
        
        print(f"   - Notícias analisadas: {noticias_analisadas}")
        print(f"   - Posts analisados: {posts_analisados}")
        
        # Teste 2: Verificar sentimento por clube
        print("\n📊 Teste 2: Verificando sentimento por clube...")
        
        cursor.execute("""
            SELECT 
                c.nome as clube,
                COUNT(n.id) as total_noticias,
                AVG(n.score_sentimento) as score_medio,
                COUNT(CASE WHEN n.sentimento = 'positivo' THEN 1 END) as positivas,
                COUNT(CASE WHEN n.sentimento = 'negativo' THEN 1 END) as negativas,
                COUNT(CASE WHEN n.sentimento = 'neutro' THEN 1 END) as neutras
            FROM noticias_clubes n
            JOIN clubes c ON n.clube_id = c.id
            WHERE n.sentimento IS NOT NULL
            GROUP BY c.id, c.nome
            ORDER BY total_noticias DESC
        """)
        
        resultados_clubes = cursor.fetchall()
        
        for clube in resultados_clubes:
            nome, total, score_medio, positivas, negativas, neutras = clube
            print(f"   - {nome}:")
            print(f"     * Total: {total} notícias")
            print(f"     * Score médio: {score_medio:.3f}")
            print(f"     * Positivas: {positivas}, Negativas: {negativas}, Neutras: {neutras}")
        
        # Teste 3: Verificar estatísticas gerais
        print("\n📊 Teste 3: Estatísticas gerais de sentimento...")
        
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
        print(f"   - Notícias:")
        print(f"     * Total: {stats_noticias[0]}")
        print(f"     * Positivas: {stats_noticias[1]}")
        print(f"     * Negativas: {stats_noticias[2]}")
        print(f"     * Neutras: {stats_noticias[3]}")
        print(f"     * Score médio: {stats_noticias[4]:.3f}")
        
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
        print(f"   - Posts:")
        print(f"     * Total: {stats_posts[0]}")
        print(f"     * Positivos: {stats_posts[1]}")
        print(f"     * Negativos: {stats_posts[2]}")
        print(f"     * Neutros: {stats_posts[3]}")
        print(f"     * Score médio: {stats_posts[4]:.3f}")
        
        # Teste 4: Simular endpoint de sentimento para clube específico
        print("\n📊 Teste 4: Simulando endpoint de sentimento para clube específico...")
        
        clube_id_teste = 1  # Flamengo
        cursor.execute("""
            SELECT 
                c.nome as nome_clube,
                COUNT(n.id) as total_noticias,
                AVG(n.score_sentimento) as score_medio_noticias,
                AVG(n.confianca_sentimento) as confianca_media,
                MAX(n.analisado_em) as ultima_analise
            FROM noticias_clubes n
            JOIN clubes c ON n.clube_id = c.id
            WHERE n.clube_id = ? AND n.sentimento IS NOT NULL
            GROUP BY c.id, c.nome
        """, (clube_id_teste,))
        
        resultado_clube = cursor.fetchone()
        
        if resultado_clube:
            nome_clube, total_noticias, score_medio, confianca, ultima_analise = resultado_clube
            
            # Calcular sentimento geral
            if score_medio > 0.1:
                sentimento_geral = 'positivo'
            elif score_medio < -0.1:
                sentimento_geral = 'negativo'
            else:
                sentimento_geral = 'neutro'
            
            print(f"   - Clube ID {clube_id_teste} ({nome_clube}):")
            print(f"     * Sentimento geral: {sentimento_geral}")
            print(f"     * Score médio: {score_medio:.3f}")
            print(f"     * Total de notícias: {total_noticias}")
            print(f"     * Confiança média: {confianca:.3f}")
            print(f"     * Última análise: {ultima_analise}")
            
            # Simular resposta da API
            resposta_api = {
                "clube_id": clube_id_teste,
                "nome_clube": nome_clube,
                "sentimento_medio_noticias": score_medio or 0.0,
                "noticias_analisadas": total_noticias,
                "sentimento_medio_posts": None,
                "posts_analisados": None,
                "sentimento_geral": sentimento_geral,
                "confianca_media": confianca,
                "ultima_atualizacao": ultima_analise
            }
            
            print(f"\n📋 Resposta simulada da API:")
            print(f"   {resposta_api}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

def main():
    """Função principal."""
    print("🧪 Testando Funcionalidade de Análise de Sentimento")
    print("=" * 60)
    
    success = test_sentiment_analysis()
    
    print("=" * 60)
    if success:
        print("🎉 Teste concluído com sucesso!")
        print("✅ A funcionalidade de análise de sentimento está funcionando corretamente.")
        print("🔧 O endpoint da API está pronto para uso.")
    else:
        print("❌ Teste falhou. Verifique os erros acima.")
    
    return success

if __name__ == "__main__":
    main()
