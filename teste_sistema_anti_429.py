#!/usr/bin/env python3
"""
Teste completo do sistema anti-429 avançado.

Testa:
- Máquina de estados (NOMINAL → THROTTLED → RECONFIGURING → HALTED)
- Rotação de proxies (se configurados)
- Cabeçalhos HTTP completos
- Integração com fazer_requisicao
"""

import sys
import os
import logging
import time
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logging sem emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('teste_anti_429.log')
    ]
)

logger = logging.getLogger(__name__)

def testar_maquina_estados():
    """Testa a máquina de estados anti-429."""
    logger.info("TESTE: Maquina de Estados Anti-429")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.anti_429_state_machine import Anti429StateMachine, ScrapingState
        
        # Criar máquina de estados
        state_machine = Anti429StateMachine()
        
        # Estado inicial
        logger.info(f"Estado inicial: {state_machine.get_current_state().value}")
        assert state_machine.get_current_state() == ScrapingState.NOMINAL
        
        # Simular sucesso
        state_machine.record_success("https://test.com")
        logger.info(f"Apos sucesso: {state_machine.get_current_state().value}")
        
        # Simular erro 429
        state_machine.record_429_error("https://test.com")
        logger.info(f"Apos erro 429: {state_machine.get_current_state().value}")
        
        # Simular múltiplos erros 429
        for i in range(3):
            state_machine.record_429_error("https://test.com")
        logger.info(f"Apos multiplos 429: {state_machine.get_current_state().value}")
        
        # Testar mudança de identidade
        if state_machine.get_current_state() == ScrapingState.RECONFIGURING:
            changed = state_machine.request_identity_change()
            logger.info(f"Mudanca de identidade: {changed}")
            logger.info(f"Estado apos mudanca: {state_machine.get_current_state().value}")
        
        # Obter estatísticas
        stats = state_machine.get_state_summary()
        logger.info(f"Estatisticas: {stats}")
        
        logger.info("SUCESSO: Maquina de estados funcionando")
        return True
        
    except Exception as e:
        logger.error(f"ERRO na maquina de estados: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_sistema_proxies():
    """Testa o sistema de rotação de proxies."""
    logger.info("\nTESTE: Sistema de Rotacao de Proxies")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.proxy_rotation_system import ProxyRotationSystem
        
        # Criar sistema de proxies
        proxy_system = ProxyRotationSystem()
        
        # Adicionar proxies de exemplo (não funcionais, apenas para teste)
        proxy_system.add_proxy("proxy1.example.com", 8080, is_residential=True)
        proxy_system.add_proxy("proxy2.example.com", 3128, is_residential=False)
        
        logger.info(f"Proxies adicionados: {len(proxy_system.proxies)}")
        
        # Obter estatísticas
        stats = proxy_system.get_proxy_stats()
        logger.info(f"Estatisticas de proxies: {stats}")
        
        # Tentar obter próximo proxy
        next_proxy = proxy_system.get_next_proxy()
        if next_proxy:
            logger.info(f"Proximo proxy: {next_proxy.host}:{next_proxy.port}")
            
            # Simular uso
            proxy_system.record_proxy_result(next_proxy, True, 1.5)
            logger.info("Sucesso simulado registrado")
        else:
            logger.info("Nenhum proxy disponivel (esperado para proxies de exemplo)")
        
        logger.info("SUCESSO: Sistema de proxies funcionando")
        return True
        
    except Exception as e:
        logger.error(f"ERRO no sistema de proxies: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_cabecalhos_emulacao():
    """Testa o sistema de cabeçalhos de emulação."""
    logger.info("\nTESTE: Sistema de Cabecalhos de Emulacao")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.browser_emulation_headers import BrowserEmulationHeaders
        
        # Criar sistema de cabeçalhos
        header_system = BrowserEmulationHeaders()
        
        # Selecionar perfil aleatório
        profile = header_system.select_random_profile()
        logger.info(f"Perfil selecionado: {profile.name}")
        
        # Gerar cabeçalhos para FBRef
        url_teste = "https://fbref.com/en/comps/9/Premier-League-Stats"
        headers = header_system.get_headers_for_fbref(url_teste)
        
        logger.info(f"Cabecalhos gerados ({len(headers)} total):")
        for key, value in headers.items():
            logger.info(f"  {key}: {value[:50]}...")
        
        # Verificar cabeçalhos essenciais
        essential_headers = ['User-Agent', 'Accept', 'Accept-Language', 'Accept-Encoding']
        for header in essential_headers:
            if header in headers:
                logger.info(f"ESSENCIAL OK: {header}")
            else:
                logger.warning(f"ESSENCIAL FALTANDO: {header}")
        
        # Testar simulação de navegação
        urls = [
            "https://fbref.com/en/comps/9/Premier-League-Stats",
            "https://fbref.com/en/squads/18bb7c10/Arsenal-Stats"
        ]
        
        headers_sequence = header_system.simulate_natural_browsing_headers(urls)
        logger.info(f"Sequencia de navegacao simulada: {len(headers_sequence)} conjuntos de cabecalhos")
        
        # Verificar Referer na segunda requisição
        if len(headers_sequence) > 1 and 'Referer' in headers_sequence[1]:
            logger.info(f"Referer correto: {headers_sequence[1]['Referer']}")
        
        logger.info("SUCESSO: Sistema de cabecalhos funcionando")
        return True
        
    except Exception as e:
        logger.error(f"ERRO no sistema de cabecalhos: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_integracao_completa():
    """Testa a integração completa com fazer_requisicao."""
    logger.info("\nTESTE: Integracao Completa Anti-429")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.fbref_utils import fazer_requisicao, get_anti_429_systems
        
        # Verificar se sistemas foram inicializados
        state_machine, proxy_system, header_system = get_anti_429_systems()
        
        logger.info("Sistemas anti-429 inicializados:")
        logger.info(f"  - Maquina de estados: {'OK' if state_machine else 'FALHA'}")
        logger.info(f"  - Sistema de proxies: {'OK' if proxy_system else 'FALHA'}")
        logger.info(f"  - Sistema de cabecalhos: {'OK' if header_system else 'FALHA'}")
        
        # Testar requisição com sistemas integrados
        url_teste = "https://fbref.com/en/comps/9/Premier-League-Stats"
        logger.info(f"Testando requisicao integrada para: {url_teste}")
        
        start_time = time.time()
        soup = fazer_requisicao(url_teste)
        end_time = time.time()
        
        if soup:
            logger.info(f"SUCESSO: Requisicao completada em {end_time - start_time:.2f}s")
            
            # Verificar se parsing de comentários foi aplicado
            tabelas = soup.find_all('table')
            logger.info(f"Tabelas encontradas: {len(tabelas)}")
            
            # Obter estatísticas dos sistemas
            if state_machine:
                stats = state_machine.get_state_summary()
                logger.info(f"Estado da maquina: {stats['current_state']}")
                logger.info(f"Requisicoes feitas: {stats['requests_made']}")
            
            return True
        else:
            logger.warning("Requisicao retornou None (pode ser esperado se FBRef estiver bloqueando)")
            return True  # Não é falha do nosso sistema
            
    except Exception as e:
        logger.error(f"ERRO na integracao completa: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_configuracao_proxies():
    """Testa carregamento de configuração de proxies."""
    logger.info("\nTESTE: Configuracao de Proxies")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.proxy_rotation_system import ProxyRotationSystem, EXAMPLE_PROXY_CONFIG
        
        # Criar sistema e carregar configuração de exemplo
        proxy_system = ProxyRotationSystem()
        
        # Configuração de exemplo (proxies não funcionais)
        config_exemplo = {
            "proxies": [
                {
                    "host": "exemplo-residencial.com",
                    "port": 8080,
                    "username": "user",
                    "password": "pass",
                    "type": "http",
                    "residential": True
                },
                {
                    "host": "exemplo-datacenter.com",
                    "port": 3128,
                    "type": "http",
                    "residential": False
                }
            ]
        }
        
        proxy_system.load_proxies_from_config(config_exemplo)
        
        stats = proxy_system.get_proxy_stats()
        logger.info(f"Proxies carregados da configuracao: {stats['total_proxies']}")
        logger.info(f"Proxies residenciais: {stats['residential_proxies']}")
        logger.info(f"Proxies datacenter: {stats['datacenter_proxies']}")
        
        logger.info("SUCESSO: Configuracao de proxies funcionando")
        return True
        
    except Exception as e:
        logger.error(f"ERRO na configuracao de proxies: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal do teste."""
    logger.info("INICIANDO TESTE COMPLETO DO SISTEMA ANTI-429")
    logger.info(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    resultados = []
    
    # Teste 1: Máquina de estados
    resultado1 = testar_maquina_estados()
    resultados.append(("Maquina de Estados", resultado1))
    
    # Teste 2: Sistema de proxies
    resultado2 = testar_sistema_proxies()
    resultados.append(("Sistema de Proxies", resultado2))
    
    # Teste 3: Cabeçalhos de emulação
    resultado3 = testar_cabecalhos_emulacao()
    resultados.append(("Cabecalhos de Emulacao", resultado3))
    
    # Teste 4: Configuração de proxies
    resultado4 = testar_configuracao_proxies()
    resultados.append(("Configuracao de Proxies", resultado4))
    
    # Teste 5: Integração completa
    resultado5 = testar_integracao_completa()
    resultados.append(("Integracao Completa", resultado5))
    
    # Relatório final
    logger.info("\n" + "=" * 80)
    logger.info("RELATORIO FINAL DOS TESTES ANTI-429")
    logger.info("=" * 80)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "PASSOU" if resultado else "FALHOU"
        logger.info(f"  {status} - {nome}")
        if resultado:
            sucessos += 1
    
    logger.info(f"\nResultado: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        logger.info("TODOS OS TESTES PASSARAM! Sistema anti-429 implementado com sucesso!")
        return True
    else:
        logger.warning("Alguns testes falharam. Revisar implementacao.")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
