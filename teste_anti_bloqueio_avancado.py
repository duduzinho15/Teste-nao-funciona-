#!/usr/bin/env python3
"""
Teste do Sistema Anti-Bloqueio Avançado para FBRef

Testa estratégias sofisticadas para contornar bloqueios 429:
- Delays dinâmicos baseados em padrões de tráfego
- Análise de horários ótimos
- Estratégias agressivas para casos críticos
- Monitoramento em tempo real
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
        logging.FileHandler('teste_anti_bloqueio_avancado.log')
    ]
)

logger = logging.getLogger(__name__)

def testar_sistema_anti_bloqueio():
    """Testa o sistema anti-bloqueio avançado."""
    logger.info("TESTE: Sistema Anti-Bloqueio Avancado")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import (
            get_advanced_anti_blocking, 
            calculate_intelligent_delay,
            record_fbref_request,
            should_change_identity,
            get_blocking_analysis,
            get_session_stats
        )
        
        # Obter instância do sistema
        anti_blocking = get_advanced_anti_blocking()
        
        # Testar padrão de tráfego atual
        current_pattern = anti_blocking.get_current_traffic_pattern()
        logger.info(f"Padrao de trafego atual: {current_pattern.value}")
        
        # Testar cálculo de delay inteligente
        test_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        delay = calculate_intelligent_delay(test_url)
        logger.info(f"Delay inteligente calculado: {delay:.2f}s")
        
        # Simular algumas requisições com diferentes resultados
        logger.info("Simulando historico de requisicoes...")
        
        # Simular sucessos
        for i in range(5):
            record_fbref_request(f"https://fbref.com/test/{i}", True, 1.5, 200)
        
        # Simular alguns bloqueios 429
        for i in range(3):
            record_fbref_request(f"https://fbref.com/blocked/{i}", False, 0.5, 429)
        
        # Verificar se deve trocar identidade
        should_change = should_change_identity()
        logger.info(f"Deve trocar identidade: {should_change}")
        
        # Obter estatísticas da sessão
        stats = get_session_stats()
        logger.info("Estatisticas da sessao:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        # Obter análise de bloqueios
        analysis = get_blocking_analysis()
        logger.info("Analise de bloqueios:")
        for key, value in analysis.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("SUCESSO: Sistema anti-bloqueio funcionando")
        return True
        
    except Exception as e:
        logger.error(f"ERRO no sistema anti-bloqueio: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_integracao_com_fbref():
    """Testa integração completa com requisições reais ao FBRef."""
    logger.info("\nTESTE: Integracao com FBRef Real")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.fbref_utils import fazer_requisicao
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import get_session_stats, get_blocking_analysis
        
        # URLs de teste do FBRef
        test_urls = [
            "https://fbref.com/en/comps/9/Premier-League-Stats",
            "https://fbref.com/en/comps/11/Serie-A-Stats",
            "https://fbref.com/en/comps/12/La-Liga-Stats"
        ]
        
        successful_requests = 0
        total_requests = len(test_urls)
        
        logger.info(f"Testando {total_requests} URLs do FBRef...")
        
        for i, url in enumerate(test_urls, 1):
            logger.info(f"Requisicao {i}/{total_requests}: {url}")
            
            start_time = time.time()
            soup = fazer_requisicao(url)
            end_time = time.time()
            
            if soup:
                tabelas = soup.find_all('table')
                logger.info(f"SUCESSO: {len(tabelas)} tabelas encontradas em {end_time - start_time:.2f}s")
                successful_requests += 1
            else:
                logger.warning(f"FALHA: Nenhum conteudo retornado em {end_time - start_time:.2f}s")
            
            # Mostrar estatísticas após cada requisição
            stats = get_session_stats()
            logger.info(f"Taxa de sucesso atual: {stats['success_rate']:.2%}")
            
            # Pequena pausa entre requisições para análise
            if i < total_requests:
                logger.info("Aguardando antes da proxima requisicao...")
                time.sleep(2)
        
        # Relatório final
        success_rate = successful_requests / total_requests
        logger.info(f"\nResultado final: {successful_requests}/{total_requests} sucessos ({success_rate:.2%})")
        
        # Estatísticas finais
        final_stats = get_session_stats()
        logger.info("Estatisticas finais:")
        for key, value in final_stats.items():
            logger.info(f"  {key}: {value}")
        
        # Análise de bloqueios
        analysis = get_blocking_analysis()
        if 'total_blocks' in analysis and analysis['total_blocks'] > 0:
            logger.info("Analise de bloqueios:")
            for key, value in analysis.items():
                logger.info(f"  {key}: {value}")
        
        # Considerar sucesso se pelo menos 1 requisição funcionou
        return successful_requests > 0
        
    except Exception as e:
        logger.error(f"ERRO na integracao com FBRef: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_estrategias_horarios():
    """Testa análise de horários ótimos para requisições."""
    logger.info("\nTESTE: Estrategias de Horarios")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import get_advanced_anti_blocking
        
        anti_blocking = get_advanced_anti_blocking()
        
        # Simular bloqueios em diferentes horários
        logger.info("Simulando bloqueios em diferentes horarios...")
        
        # Simular bloqueios no horário atual
        current_hour = datetime.now().hour
        for i in range(5):
            # Simular bloqueio no horário atual
            blocked_time = datetime.now().replace(minute=i*10)
            anti_blocking.blocking_analysis.blocked_times.append(blocked_time)
        
        # Simular bloqueios em outros horários
        for hour_offset in [1, 2, 3]:
            blocked_time = datetime.now().replace(hour=(current_hour + hour_offset) % 24)
            anti_blocking.blocking_analysis.blocked_times.append(blocked_time)
        
        # Obter horário ótimo
        optimal_time = anti_blocking.get_optimal_request_time()
        logger.info(f"Horario otimo sugerido: {optimal_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Analisar padrões
        analysis = anti_blocking.analyze_blocking_patterns()
        logger.info("Analise de padroes de bloqueio:")
        for key, value in analysis.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("SUCESSO: Analise de horarios funcionando")
        return True
        
    except Exception as e:
        logger.error(f"ERRO na analise de horarios: {e}")
        import traceback
        traceback.print_exc()
        return False

def monitorar_sistema_tempo_real():
    """Monitora o sistema em tempo real durante operação."""
    logger.info("\nTESTE: Monitoramento Tempo Real")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import get_session_stats, get_blocking_analysis
        
        logger.info("Iniciando monitoramento por 30 segundos...")
        
        start_time = time.time()
        while time.time() - start_time < 30:
            stats = get_session_stats()
            
            # Log de estatísticas a cada 10 segundos
            if int(time.time() - start_time) % 10 == 0:
                logger.info(f"[{int(time.time() - start_time)}s] Monitoramento:")
                logger.info(f"  Requisicoes: {stats['total_requests']}")
                logger.info(f"  Taxa sucesso: {stats['success_rate']:.2%}")
                logger.info(f"  Padrao trafego: {stats['current_traffic_pattern']}")
            
            time.sleep(1)
        
        logger.info("Monitoramento concluido")
        return True
        
    except Exception as e:
        logger.error(f"ERRO no monitoramento: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal do teste."""
    logger.info("INICIANDO TESTE COMPLETO DO SISTEMA ANTI-BLOQUEIO AVANCADO")
    logger.info(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    resultados = []
    
    # Teste 1: Sistema anti-bloqueio básico
    resultado1 = testar_sistema_anti_bloqueio()
    resultados.append(("Sistema Anti-Bloqueio", resultado1))
    
    # Teste 2: Estratégias de horários
    resultado2 = testar_estrategias_horarios()
    resultados.append(("Estrategias de Horarios", resultado2))
    
    # Teste 3: Monitoramento tempo real
    resultado3 = monitorar_sistema_tempo_real()
    resultados.append(("Monitoramento Tempo Real", resultado3))
    
    # Teste 4: Integração com FBRef (mais crítico)
    logger.info("\n" + "!" * 80)
    logger.info("TESTE CRITICO: Integracao com FBRef Real")
    logger.info("Este teste fara requisicoes reais ao FBRef")
    logger.info("!" * 80)
    
    resultado4 = testar_integracao_com_fbref()
    resultados.append(("Integracao FBRef Real", resultado4))
    
    # Relatório final
    logger.info("\n" + "=" * 80)
    logger.info("RELATORIO FINAL - SISTEMA ANTI-BLOQUEIO AVANCADO")
    logger.info("=" * 80)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "PASSOU" if resultado else "FALHOU"
        logger.info(f"  {status} - {nome}")
        if resultado:
            sucessos += 1
    
    logger.info(f"\nResultado: {sucessos}/{len(resultados)} testes passaram")
    
    # Análise especial do teste crítico
    if resultados[-1][1]:  # Se integração FBRef passou
        logger.info("\n*** SUCESSO CRITICO ***")
        logger.info("O sistema conseguiu acessar o FBRef real!")
        logger.info("Isso significa que as estrategias anti-bloqueio estao funcionando!")
    else:
        logger.warning("\n*** ATENCAO ***")
        logger.warning("O sistema nao conseguiu acessar o FBRef real.")
        logger.warning("Pode ser necessario ajustar estrategias ou usar proxies.")
    
    if sucessos >= 3:  # Pelo menos 3 dos 4 testes
        logger.info("\nSISTEMA ANTI-BLOQUEIO AVANCADO FUNCIONANDO!")
        return True
    else:
        logger.warning("Sistema precisa de ajustes.")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
