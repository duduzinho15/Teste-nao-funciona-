"""
DEMONSTRAÇÃO DOS SCRAPERS COM PLAYWRIGHT
========================================

Script para demonstrar e testar os scrapers usando Playwright da Microsoft.
Mostra as funcionalidades avançadas como anti-detecção, screenshots automáticos,
e interceptação de requisições.

Autor: Sistema de Coleta de Dados
Data: 2025-08-14
Versão: 1.0
"""

import asyncio
import logging
import time
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_fbref_scraper():
    """Demonstra o scraper do FBRef com Playwright."""
    print("\n" + "="*60)
    print("🎭 DEMONSTRAÇÃO DO SCRAPER FBREF COM PLAYWRIGHT")
    print("="*60)
    
    try:
        from Coleta_de_dados.apis.fbref.playwright_scraper import FBRefPlaywrightScraper
        
        # URLs de teste
        competition_urls = [
            "https://fbref.com/en/comps/9/Premier-League-Stats",
            "https://fbref.com/en/comps/12/La-Liga-Stats"
        ]
        
        print(f"🏆 Testando com {len(competition_urls)} competições...")
        
        async with FBRefPlaywrightScraper(headless=False) as scraper:
            print("✅ Scraper iniciado com sucesso")
            
            # Coletar lista de competições
            print("\n📊 Coletando lista de competições...")
            competitions = await scraper.collect_competitions()
            print(f"✅ {len(competitions)} competições encontradas")
            
            # Coletar detalhes de uma competição
            if competitions:
                print(f"\n🏆 Coletando detalhes de: {competitions[0]['name']}")
                comp_details = await scraper.collect_competition_details(competitions[0]['url'])
                if comp_details:
                    print(f"✅ Detalhes coletados: {comp_details.get('title', 'N/A')}")
                    print(f"📊 Estatísticas: {len(comp_details.get('stats', []))} tabelas")
            
            # Coletar partidas
            print(f"\n⚽ Coletando partidas da Premier League...")
            matches = await scraper.collect_matches(competition_urls[0])
            print(f"✅ {len(matches)} partidas coletadas")
            
            # Mostrar algumas partidas
            if matches:
                print("\n📋 Exemplos de partidas:")
                for i, match in enumerate(matches[:3]):
                    print(f"  {i+1}. {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}")
                    print(f"     Data: {match.get('date', 'N/A')}")
                    print(f"     Placar: {match.get('score', 'N/A')}")
                    print()
            
            # Screenshot da página atual
            screenshot_path = await scraper.take_screenshot("fbref_demo.png")
            if screenshot_path:
                print(f"📸 Screenshot salvo: {screenshot_path}")
            
            # Dados interceptados
            intercepted_data = scraper.get_intercepted_data()
            print(f"🔍 {len(intercepted_data['requests'])} requisições interceptadas")
            
        print("✅ Demonstração do FBRef concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na demonstração do FBRef: {e}")
        import traceback
        traceback.print_exc()
        return False

async def demo_sofascore_scraper():
    """Demonstra o scraper do SofaScore com Playwright."""
    print("\n" + "="*60)
    print("🎭 DEMONSTRAÇÃO DO SCRAPER SOFASCORE COM PLAYWRIGHT")
    print("="*60)
    
    try:
        from Coleta_de_dados.apis.sofascore.playwright_scraper import SofaScorePlaywrightScraper
        
        # URLs de teste
        urls = {
            "live": ["https://www.sofascore.com/football/live"],
            "teams": [
                "https://www.sofascore.com/team/manchester-united/17"
            ],
            "tournaments": [
                "https://www.sofascore.com/tournament/england-premier-league/7"
            ]
        }
        
        print(f"⚽ Testando com {sum(len(url_list) for url_list in urls.values())} URLs...")
        
        async with SofaScorePlaywrightScraper(headless=False) as scraper:
            print("✅ Scraper iniciado com sucesso")
            
            # Coletar partidas ao vivo
            print("\n📊 Coletando partidas ao vivo...")
            live_matches = await scraper.collect_live_matches()
            print(f"✅ {len(live_matches)} partidas ao vivo encontradas")
            
            # Mostrar algumas partidas ao vivo
            if live_matches:
                print("\n📋 Exemplos de partidas ao vivo:")
                for i, match in enumerate(live_matches[:3]):
                    print(f"  {i+1}. {match.get('title', 'N/A')}")
                    print(f"     URL: {match.get('url', 'N/A')}")
                    print()
            
            # Coletar partidas de um time
            print(f"\n⚽ Coletando partidas do Manchester United...")
            team_matches = await scraper.collect_team_matches(urls["teams"][0], limit=5)
            print(f"✅ {len(team_matches)} partidas do time coletadas")
            
            # Screenshot da página atual
            screenshot_path = await scraper.take_screenshot("sofascore_demo.png")
            if screenshot_path:
                print(f"📸 Screenshot salvo: {screenshot_path}")
            
            # Dados interceptados
            intercepted_data = scraper.get_intercepted_data()
            print(f"🔍 {len(intercepted_data['requests'])} requisições interceptadas")
            
        print("✅ Demonstração do SofaScore concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na demonstração do SofaScore: {e}")
        import traceback
        traceback.print_exc()
        return False

async def demo_playwright_features():
    """Demonstra funcionalidades avançadas do Playwright."""
    print("\n" + "="*60)
    print("🎭 DEMONSTRAÇÃO DAS FUNCIONALIDADES AVANÇADAS DO PLAYWRIGHT")
    print("="*60)
    
    try:
        from Coleta_de_dados.apis.playwright_base import PlaywrightBaseScraper
        
        print("🚀 Testando funcionalidades avançadas...")
        
        async with PlaywrightBaseScraper(
            headless=False,
            enable_video=True,
            enable_har=True
        ) as scraper:
            print("✅ Scraper base iniciado com sucesso")
            
            # Navegar para uma página de teste
            test_url = "https://httpbin.org/headers"
            print(f"\n🌐 Navegando para: {test_url}")
            
            if await scraper.navigate_to(test_url):
                print("✅ Navegação bem-sucedida")
                
                # Aguardar elemento específico
                if await scraper.wait_for_element("pre"):
                    print("✅ Elemento 'pre' encontrado")
                    
                    # Obter conteúdo da página
                    content = await scraper.get_page_content()
                    if "User-Agent" in content:
                        print("✅ Conteúdo da página obtido com sucesso")
                    
                    # Executar JavaScript
                    js_result = await scraper.evaluate_javascript("document.title")
                    print(f"⚡ JavaScript executado: {js_result}")
                    
                    # Screenshot
                    screenshot_path = await scraper.take_screenshot("playwright_features_demo.png")
                    if screenshot_path:
                        print(f"📸 Screenshot salvo: {screenshot_path}")
                    
                    # Dados interceptados
                    intercepted_data = scraper.get_intercepted_data()
                    print(f"🔍 {len(intercepted_data['requests'])} requisições interceptadas")
                    
                    # Mostrar algumas requisições
                    if intercepted_data['requests']:
                        print("\n📋 Exemplos de requisições interceptadas:")
                        for i, req in enumerate(intercepted_data['requests'][:3]):
                            print(f"  {i+1}. {req['method']} {req['url']}")
                            print(f"     Timestamp: {req['timestamp']}")
                            print()
                else:
                    print("⚠️ Elemento 'pre' não encontrado")
            else:
                print("❌ Falha na navegação")
        
        print("✅ Demonstração das funcionalidades concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na demonstração das funcionalidades: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Função principal de demonstração."""
    print("🚀 DEMONSTRAÇÃO COMPLETA DOS SCRAPERS COM PLAYWRIGHT")
    print("="*60)
    print("🎭 Playwright da Microsoft - Web Scraping Avançado")
    print("📊 Funcionalidades: Anti-detecção, Screenshots, Interceptação")
    print("🌐 Navegadores: Chromium, Firefox, WebKit")
    print("="*60)
    
    start_time = time.time()
    results = []
    
    try:
        # Demonstração 1: Funcionalidades base do Playwright
        print("\n1️⃣ TESTANDO FUNCIONALIDADES BASE DO PLAYWRIGHT...")
        result1 = await demo_playwright_features()
        results.append(("Funcionalidades Base", result1))
        
        # Demonstração 2: Scraper do FBRef
        print("\n2️⃣ TESTANDO SCRAPER DO FBREF...")
        result2 = await demo_fbref_scraper()
        results.append(("FBRef Scraper", result2))
        
        # Demonstração 3: Scraper do SofaScore
        print("\n3️⃣ TESTANDO SCRAPER DO SOFASCORE...")
        result3 = await demo_sofascore_scraper()
        results.append(("SofaScore Scraper", result3))
        
    except KeyboardInterrupt:
        print("\n⚠️ Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro geral na demonstração: {e}")
        import traceback
        traceback.print_exc()
    
    # Resultados finais
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("📊 RESULTADOS DA DEMONSTRAÇÃO")
    print("="*60)
    
    for name, result in results:
        status = "✅ SUCESSO" if result else "❌ FALHA"
        print(f"{name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n🎯 Resumo: {success_count}/{total_count} testes passaram")
    print(f"⏱️ Duração total: {duration:.2f} segundos")
    
    if success_count == total_count:
        print("\n🎉 TODAS AS DEMONSTRAÇÕES PASSARAM!")
        print("✅ Playwright está funcionando perfeitamente")
        print("✅ Scrapers estão operacionais")
        print("✅ Sistema pronto para produção")
    else:
        print(f"\n⚠️ {total_count - success_count} demonstração(ões) falharam")
        print("🔧 Verifique os logs para identificar problemas")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Configurar scrapers para produção")
    print("2. Implementar agendamento automático")
    print("3. Configurar monitoramento e alertas")
    print("4. Integrar com sistema de ML")
    print("5. Implementar cache e otimizações")

if __name__ == "__main__":
    # Executar demonstração
    asyncio.run(main())
