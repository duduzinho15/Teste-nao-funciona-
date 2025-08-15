"""
TESTE RÁPIDO DO PLAYWRIGHT
===========================

Script simples para testar se o Playwright está funcionando corretamente.
"""

import asyncio
import sys
from pathlib import Path

async def test_playwright_basic():
    """Teste básico do Playwright."""
    try:
        print("🧪 Testando instalação básica do Playwright...")
        
        from playwright.async_api import async_playwright
        
        print("✅ Importação bem-sucedida")
        
        async with async_playwright() as p:
            print("✅ Playwright iniciado")
            
            browser = await p.chromium.launch(headless=True)
            print("✅ Navegador Chromium iniciado")
            
            page = await browser.new_page()
            print("✅ Nova página criada")
            
            await page.goto("https://httpbin.org/status/200")
            print("✅ Navegação bem-sucedida")
            
            title = await page.title()
            print(f"✅ Título da página: {title}")
            
            await browser.close()
            print("✅ Navegador fechado")
            
        print("✅ Teste básico concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste básico: {e}")
        return False

async def test_playwright_base_scraper():
    """Teste da classe base do scraper."""
    try:
        print("\n🧪 Testando classe base do scraper...")
        
        # Adicionar o diretório ao path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from Coleta_de_dados.apis.playwright_base import PlaywrightBaseScraper
        
        print("✅ Classe base importada")
        
        async with PlaywrightBaseScraper(headless=True) as scraper:
            print("✅ Scraper base iniciado")
            
            # Testar navegação
            success = await scraper.navigate_to("https://httpbin.org/headers")
            if success:
                print("✅ Navegação bem-sucedida")
                
                # Testar screenshot
                screenshot_path = await scraper.take_screenshot("test_quick.png")
                if screenshot_path:
                    print(f"✅ Screenshot salvo: {screenshot_path}")
                
                # Testar obtenção de conteúdo
                content = await scraper.get_page_content()
                if content and len(content) > 100:
                    print("✅ Conteúdo da página obtido")
                else:
                    print("⚠️ Conteúdo da página muito pequeno")
                
                # Testar JavaScript
                js_result = await scraper.evaluate_javascript("document.title")
                if js_result:
                    print(f"✅ JavaScript executado: {js_result}")
                
                # Testar dados interceptados
                intercepted = scraper.get_intercepted_data()
                print(f"✅ Requisições interceptadas: {len(intercepted['requests'])}")
                
            else:
                print("❌ Falha na navegação")
                return False
        
        print("✅ Teste da classe base concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da classe base: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Função principal de teste."""
    print("🚀 TESTE RÁPIDO DO PLAYWRIGHT")
    print("="*40)
    
    results = []
    
    # Teste 1: Instalação básica
    print("\n1️⃣ TESTE DE INSTALAÇÃO BÁSICA")
    result1 = await test_playwright_basic()
    results.append(("Instalação Básica", result1))
    
    # Teste 2: Classe base do scraper
    print("\n2️⃣ TESTE DA CLASSE BASE")
    result2 = await test_playwright_base_scraper()
    results.append(("Classe Base", result2))
    
    # Resultados
    print("\n" + "="*40)
    print("📊 RESULTADOS DOS TESTES")
    print("="*40)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n🎯 Resumo: {success_count}/{total_count} testes passaram")
    
    if success_count == total_count:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Playwright está funcionando perfeitamente")
        print("✅ Sistema de scrapers está operacional")
        print("✅ Pode executar a demonstração completa")
    else:
        print(f"\n⚠️ {total_count - success_count} teste(s) falharam")
        print("🔧 Verifique os erros acima")
    
    return success_count == total_count

if __name__ == "__main__":
    # Executar testes
    success = asyncio.run(main())
    
    # Código de saída
    sys.exit(0 if success else 1)
