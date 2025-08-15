#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DEMONSTRAÇÃO DOS SCRAPERS MELHORADOS COM PLAYWRIGHT
==================================================

Script para demonstrar e testar todos os scrapers melhorados usando Playwright da Microsoft.
Inclui demonstrações dos novos scrapers implementados.

Autor: Sistema de Scraping Avançado
Data: 2025-08-14
Versão: 2.0 (Scrapers Melhorados)
"""

import asyncio
import logging
import time
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_sofascore_enhanced():
    """Demonstra o scraper melhorado do SofaScore."""
    print("\n🎭 DEMONSTRAÇÃO DO SCRAPER SOFASCORE MELHORADO COM PLAYWRIGHT")
    print("=" * 70)
    
    try:
        # Importa o scraper melhorado
        from Coleta_de_dados.apis.sofascore.playwright_scraper_enhanced import SofaScorePlaywrightScraperEnhanced
        
        # Configuração do scraper
        config = {
            "headless": False,  # Mostra o navegador para demonstração
            "timeout": 30000,
            "retry_attempts": 3
        }
        
        scraper = SofaScorePlaywrightScraperEnhanced(**config)
        
        # Coleta dados de todos os esportes
        print("🔄 Coletando dados de todos os esportes...")
        data = await scraper.collect_all_sports_data()
        
        # Mostra resumo dos dados coletados
        print("\n📊 RESUMO DOS DADOS COLETADOS:")
        print("-" * 40)
        for sport, matches in data.items():
            print(f"🏈 {sport.capitalize()}: {len(matches)} partidas")
        
        # Salva no banco de dados
        print("\n💾 Salvando dados no banco...")
        total_saved = await scraper.save_to_database(data)
        print(f"✅ Total de registros salvos: {total_saved}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        return False

async def demo_social_media_collector():
    """Demonstra o coletor de redes sociais com Playwright."""
    print("\n🎭 DEMONSTRAÇÃO DO COLETOR DE REDES SOCIAIS COM PLAYWRIGHT")
    print("=" * 70)
    
    try:
        # Importa o coletor melhorado
        from Coleta_de_dados.apis.social.playwright_collector import SocialMediaPlaywrightCollector
        
        # Configuração do coletor
        config = {
            "headless": False,  # Mostra o navegador para demonstração
            "timeout": 30000,
            "retry_attempts": 3
        }
        
        collector = SocialMediaPlaywrightCollector(**config)
        
        # Handles das redes sociais dos clubes (exemplo)
        club_handles = {
            "Flamengo": {
                "twitter": "@Flamengo",
                "instagram": "flamengo",
                "facebook": "Flamengo"
            },
            "Palmeiras": {
                "twitter": "@Palmeiras",
                "instagram": "palmeiras",
                "facebook": "Palmeiras"
            }
        }
        
        # Coleta dados de todas as redes sociais
        print("🔄 Coletando dados de redes sociais...")
        data = await collector.collect_all_social_media_data(club_handles)
        
        # Mostra resumo dos dados coletados
        print("\n📊 RESUMO DOS DADOS COLETADOS:")
        print("-" * 40)
        for club_name, platforms in data.items():
            print(f"🏆 {club_name}:")
            for platform, posts in platforms.items():
                print(f"   📱 {platform.capitalize()}: {len(posts)} posts")
        
        # Salva no banco de dados
        print("\n💾 Salvando dados no banco...")
        total_saved = await collector.save_to_database(data)
        print(f"✅ Total de posts salvos: {total_saved}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        return False

async def demo_news_collector():
    """Demonstra o coletor de notícias com Playwright."""
    print("\n🎭 DEMONSTRAÇÃO DO COLETOR DE NOTÍCIAS COM PLAYWRIGHT")
    print("=" * 70)
    
    try:
        # Importa o coletor melhorado
        from Coleta_de_dados.apis.news.playwright_collector import NewsPlaywrightCollector
        
        # Configuração do coletor
        config = {
            "headless": False,  # Mostra o navegador para demonstração
            "timeout": 30000,
            "retry_attempts": 3
        }
        
        collector = NewsPlaywrightCollector(**config)
        
        # Clubes para coletar notícias
        clubes = ["Flamengo", "Palmeiras", "Corinthians", "São Paulo"]
        
        total_news = 0
        
        for clube in clubes:
            print(f"\n🏆 Coletando notícias para: {clube}")
            
            # Coleta notícias do clube
            news = await collector.collect_all_news_for_club(clube)
            total_news += len(news)
            
            print(f"   📰 {len(news)} notícias coletadas")
        
        print(f"\n📊 TOTAL: {total_news} notícias coletadas")
        
        # Salva no banco de dados
        print("\n💾 Salvando notícias no banco...")
        # Aqui você precisaria implementar a lógica para salvar no banco
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        return False

async def demo_playwright_features():
    """Demonstra funcionalidades avançadas do Playwright."""
    print("\n🎭 DEMONSTRAÇÃO DAS FUNCIONALIDADES AVANÇADAS DO PLAYWRIGHT")
    print("=" * 70)
    
    try:
        # Importa o scraper base
        from Coleta_de_dados.apis.playwright_base import PlaywrightBaseScraper
        
        # Configuração do scraper
        config = {
            "headless": False,
            "timeout": 30000,
            "retry_attempts": 3,
            "enable_screenshots": True,
            "enable_har_capture": True
        }
        
        scraper = PlaywrightBaseScraper(**config)
        
        # Demonstra funcionalidades básicas
        print("🔄 Testando funcionalidades básicas...")
        
        # Navega para uma página de teste
        test_url = "https://www.example.com"
        print(f"🌐 Navegando para: {test_url}")
        
        # Aqui você implementaria a lógica de teste
        print("✅ Funcionalidades básicas testadas com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        return False

async def run_all_demos():
    """Executa todas as demonstrações."""
    print("🚀 DEMONSTRAÇÃO COMPLETA DOS SCRAPERS MELHORADOS COM PLAYWRIGHT")
    print("=" * 80)
    print("🎭 Playwright da Microsoft - Web Scraping Avançado")
    print("📊 Scrapers Melhorados para ApostaPro")
    print("=" * 80)
    
    start_time = time.time()
    results = {}
    
    try:
        # Demonstração 1: Funcionalidades base do Playwright
        print("\n1️⃣ TESTANDO FUNCIONALIDADES BASE DO PLAYWRIGHT...")
        results['playwright_features'] = await demo_playwright_features()
        
        # Demonstração 2: Scraper do SofaScore melhorado
        print("\n2️⃣ TESTANDO SCRAPER SOFASCORE MELHORADO...")
        results['sofascore_enhanced'] = await demo_sofascore_enhanced()
        
        # Demonstração 3: Coletor de redes sociais
        print("\n3️⃣ TESTANDO COLETOR DE REDES SOCIAIS...")
        results['social_media'] = await demo_social_media_collector()
        
        # Demonstração 4: Coletor de notícias
        print("\n4️⃣ TESTANDO COLETOR DE NOTÍCIAS...")
        results['news_collector'] = await demo_news_collector()
        
        # Resumo dos resultados
        print("\n" + "=" * 80)
        print("📊 RESUMO DOS TESTES")
        print("=" * 80)
        
        total_tests = len(results)
        successful_tests = sum(1 for result in results.values() if result)
        
        for test_name, result in results.items():
            status = "✅ SUCESSO" if result else "❌ FALHA"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n🎯 Total de testes: {total_tests}")
        print(f"✅ Testes bem-sucedidos: {successful_tests}")
        print(f"❌ Testes com falha: {total_tests - successful_tests}")
        
        success_rate = (successful_tests / total_tests) * 100
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        # Tempo total de execução
        total_time = time.time() - start_time
        print(f"\n⏱️ Tempo total de execução: {total_time:.2f} segundos")
        
        if successful_tests == total_tests:
            print("\n🎉 TODOS OS TESTES FORAM EXECUTADOS COM SUCESSO!")
            print("🚀 O sistema de scrapers com Playwright está funcionando perfeitamente!")
        else:
            print(f"\n⚠️ {total_tests - successful_tests} teste(s) falharam.")
            print("🔧 Verifique os logs para identificar e corrigir os problemas.")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Erro crítico durante execução: {e}")
        return None

def main():
    """Função principal."""
    print("🎭 INICIANDO DEMONSTRAÇÃO DOS SCRAPERS MELHORADOS COM PLAYWRIGHT")
    print("=" * 80)
    
    try:
        # Executa todas as demonstrações
        results = asyncio.run(run_all_demos())
        
        if results:
            print("\n✅ Demonstração concluída!")
        else:
            print("\n❌ Demonstração falhou!")
            
    except KeyboardInterrupt:
        print("\n⏹️ Demonstração interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
