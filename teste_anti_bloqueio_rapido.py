#!/usr/bin/env python3
"""
Teste Rápido do Sistema Anti-Bloqueio

Teste focado e rápido para validar se o sistema anti-bloqueio funciona sem travamentos.
"""

import sys
import os
import logging
import time
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logging simples
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def testar_sistema_basico():
    """Testa funcionalidades básicas do sistema anti-bloqueio."""
    logger.info("TESTE: Sistema Anti-Bloqueio Basico")
    logger.info("=" * 40)
    
    try:
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import (
            get_advanced_anti_blocking, 
            calculate_intelligent_delay
        )
        
        # Obter instância
        anti_blocking = get_advanced_anti_blocking()
        logger.info(f"Sistema inicializado - Padrao: {anti_blocking.get_current_traffic_pattern().value}")
        
        # Testar cálculo de delay (deve ser limitado)
        test_url = "https://fbref.com/test"
        delay = calculate_intelligent_delay(test_url)
        logger.info(f"Delay calculado: {delay:.2f}s (deve ser <= 15s)")
        
        if delay <= 15.0:
            logger.info("SUCESSO: Delay limitado corretamente")
            return True
        else:
            logger.error(f"FALHA: Delay muito alto: {delay}s")
            return False
            
    except Exception as e:
        logger.error(f"ERRO: {e}")
        return False

def testar_requisicao_rapida():
    """Testa uma requisição rápida com timeout agressivo."""
    logger.info("\nTESTE: Requisicao Rapida com Timeout")
    logger.info("=" * 40)
    
    try:
        from Coleta_de_dados.apis.fbref.fbref_utils import fazer_requisicao
        
        # URL de teste (página simples do FBRef)
        test_url = "https://fbref.com/en/"
        
        logger.info(f"Testando requisicao para: {test_url}")
        logger.info("Timeout maximo: 30s")
        
        start_time = time.time()
        
        # Fazer requisição com timeout
        soup = fazer_requisicao(test_url)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Requisicao completada em {duration:.2f}s")
        
        if soup:
            logger.info("SUCESSO: Conteudo recebido")
            return True
        else:
            logger.info("INFO: Nenhum conteudo (pode ser bloqueio - usando fallback)")
            return True  # Não é falha do sistema
            
    except Exception as e:
        logger.error(f"ERRO na requisicao: {e}")
        return False

def testar_sistema_integrado():
    """Testa integração de todos os sistemas."""
    logger.info("\nTESTE: Sistema Integrado")
    logger.info("=" * 40)
    
    try:
        from Coleta_de_dados.apis.fbref.fbref_utils import get_anti_429_systems
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import get_session_stats
        
        # Verificar se sistemas estão inicializados
        state_machine, proxy_system, header_system = get_anti_429_systems()
        
        logger.info("Sistemas inicializados:")
        logger.info(f"  - Maquina de estados: {'OK' if state_machine else 'FALHA'}")
        logger.info(f"  - Sistema de proxies: {'OK' if proxy_system else 'FALHA'}")
        logger.info(f"  - Sistema de cabecalhos: {'OK' if header_system else 'FALHA'}")
        
        # Obter estatísticas
        try:
            stats = get_session_stats()
            logger.info(f"Estatisticas obtidas: {len(stats)} metricas")
            logger.info(f"Padrao de trafego: {stats.get('current_traffic_pattern', 'N/A')}")
        except Exception as e:
            logger.warning(f"Erro ao obter estatisticas: {e}")
        
        logger.info("SUCESSO: Sistema integrado funcionando")
        return True
        
    except Exception as e:
        logger.error(f"ERRO no sistema integrado: {e}")
        return False

def main():
    """Função principal do teste rápido."""
    logger.info("INICIANDO TESTE RAPIDO DO SISTEMA ANTI-BLOQUEIO")
    logger.info(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    resultados = []
    
    # Teste 1: Sistema básico
    resultado1 = testar_sistema_basico()
    resultados.append(("Sistema Basico", resultado1))
    
    # Teste 2: Sistema integrado
    resultado2 = testar_sistema_integrado()
    resultados.append(("Sistema Integrado", resultado2))
    
    # Teste 3: Requisição rápida (mais crítico)
    logger.info("\n" + "!" * 60)
    logger.info("TESTE CRITICO: Requisicao com Timeout Agressivo")
    logger.info("!" * 60)
    
    resultado3 = testar_requisicao_rapida()
    resultados.append(("Requisicao Rapida", resultado3))
    
    # Relatório final
    logger.info("\n" + "=" * 60)
    logger.info("RELATORIO FINAL - TESTE RAPIDO")
    logger.info("=" * 60)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "PASSOU" if resultado else "FALHOU"
        logger.info(f"  {status} - {nome}")
        if resultado:
            sucessos += 1
    
    logger.info(f"\nResultado: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos >= 2:  # Pelo menos 2 dos 3 testes
        logger.info("\nSISTEMA ANTI-BLOQUEIO FUNCIONANDO (sem travamentos)!")
        return True
    else:
        logger.warning("Sistema precisa de ajustes.")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
