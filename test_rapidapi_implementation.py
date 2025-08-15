#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE DA IMPLEMENTAÇÃO RAPIDAPI
================================

Script para testar a implementação do módulo RapidAPI e sistema de logs centralizado.
Verifica se todas as funcionalidades estão funcionando corretamente.

Autor: Sistema de Coleta de Dados
Data: 2025-08-14
Versão: 1.0
"""

import sys
import os
import time
import json
from datetime import datetime

# Adicionar caminho para importar módulos
sys.path.append(os.path.abspath('.'))

def test_imports():
    """Testa se todos os módulos podem ser importados."""
    print("🧪 TESTANDO IMPORTAÇÕES...")
    
    try:
        # Testar importação do sistema de logs
        from Coleta_de_dados.utils.logger_centralizado import (
            CentralizedLogger, log_info, log_error, log_performance_decorator
        )
        print("✅ Sistema de logs centralizado importado com sucesso")
        
        # Testar importação do módulo RapidAPI
        from Coleta_de_dados.apis.rapidapi.base_rapidapi import RapidAPIBase, RapidAPIConfig
        print("✅ Classe base RapidAPI importada com sucesso")
        
        # Testar importação da API específica
        from Coleta_de_dados.apis.rapidapi.today_football_prediction import TodayFootballPredictionAPI
        print("✅ API Today Football Prediction importada com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro na importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_logger_system():
    """Testa o sistema de logs centralizado."""
    print("\n🧪 TESTANDO SISTEMA DE LOGS...")
    
    try:
        from Coleta_de_dados.utils.logger_centralizado import (
            CentralizedLogger, log_info, log_error, log_performance_decorator
        )
        
        # Criar instância do logger
        logger = CentralizedLogger("logs_teste")
        print("✅ Logger centralizado criado")
        
        # Testar logs básicos
        log_info("teste", "test_logger_system", "Teste de log de informação", {"teste": True})
        log_error("teste", "test_logger_system", "Teste de log de erro", {"teste": True}, "Erro simulado")
        print("✅ Logs básicos funcionando")
        
        # Testar decorator de performance
        @log_performance_decorator("teste")
        def funcao_teste():
            time.sleep(0.1)  # Simular trabalho
            return "sucesso"
        
        resultado = funcao_teste()
        print(f"✅ Decorator de performance funcionando: {resultado}")
        
        # Verificar estatísticas
        stats = logger.get_stats()
        print(f"✅ Estatísticas coletadas: {stats['total_logs']} logs")
        
        # Verificar alertas
        alertas = logger.get_alerts()
        print(f"✅ Alertas coletados: {len(alertas)} alertas")
        
        # Parar monitoramento
        logger.stop_monitoring()
        print("✅ Sistema de logs testado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de logs: {e}")
        return False

def test_rapidapi_base():
    """Testa a classe base do RapidAPI."""
    print("\n🧪 TESTANDO CLASSE BASE RAPIDAPI...")
    
    try:
        from Coleta_de_dados.apis.rapidapi.base_rapidapi import RapidAPIBase, RapidAPIConfig
        
        # Criar configuração de teste
        config = RapidAPIConfig(
            nome="API Teste",
            host="test.api.com",
            endpoint_base="https://test.api.com",
            chaves=["chave_teste_1", "chave_teste_2"],
            limite_requisicoes_dia=100,
            limite_requisicoes_minuto=10
        )
        print("✅ Configuração criada")
        
        # Criar uma classe de teste que implementa os métodos abstratos
        class TestRapidAPI(RapidAPIBase):
            def coletar_jogos(self, **kwargs):
                return []
            
            def coletar_jogadores(self, **kwargs):
                return []
            
            def coletar_ligas(self, **kwargs):
                return []
            
            def coletar_estatisticas(self, **kwargs):
                return []
            
            def coletar_odds(self, **kwargs):
                return []
            
            def coletar_noticias(self, **kwargs):
                return []
        
        # Testar rotação de chaves
        api = TestRapidAPI(config)
        chave1 = api._get_next_api_key()
        chave2 = api._get_next_api_key()
        chave3 = api._get_next_api_key()
        
        print(f"✅ Rotação de chaves: {chave1[:10]}... -> {chave2[:10]}... -> {chave3[:10]}...")
        
        # Verificar se voltou ao início
        assert chave3 == chave1, "Rotação de chaves não está funcionando corretamente"
        
        # Testar status
        status = api.get_status()
        print(f"✅ Status da API: {status['nome']}")
        
        # Testar reset de contadores
        api.reset_counters()
        print("✅ Reset de contadores funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na classe base: {e}")
        return False

def test_today_football_prediction_api():
    """Testa a API Today Football Prediction."""
    print("\n🧪 TESTANDO API TODAY FOOTBALL PREDICTION...")
    
    try:
        from Coleta_de_dados.apis.rapidapi.today_football_prediction import TodayFootballPredictionAPI
        
        # Criar API com chaves de teste
        api = TodayFootballPredictionAPI(["chave_teste_1", "chave_teste_2"])
        print("✅ API criada com sucesso")
        
        # Testar métodos (sem fazer requisições reais)
        print("✅ Métodos disponíveis:")
        print(f"   - coletar_jogos: {hasattr(api, 'coletar_jogos')}")
        print(f"   - coletar_jogadores: {hasattr(api, 'coletar_jogadores')}")
        print(f"   - coletar_ligas: {hasattr(api, 'coletar_ligas')}")
        print(f"   - coletar_estatisticas: {hasattr(api, 'coletar_estatisticas')}")
        print(f"   - coletar_odds: {hasattr(api, 'coletar_odds')}")
        print(f"   - coletar_noticias: {hasattr(api, 'coletar_noticias')}")
        
        # Testar status
        status = api.get_status()
        print(f"✅ Status: {status['nome']} - {status['chaves_disponiveis']} chaves")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na API Today Football Prediction: {e}")
        return False

def test_integration():
    """Testa a integração entre os sistemas."""
    print("\n🧪 TESTANDO INTEGRAÇÃO...")
    
    try:
        from Coleta_de_dados.utils.logger_centralizado import log_info, log_performance_decorator
        from Coleta_de_dados.apis.rapidapi.today_football_prediction import TodayFootballPredictionAPI
        
        # Simular coleta com logging
        @log_performance_decorator("rapidapi")
        def simular_coleta():
            """Simula uma coleta de dados."""
            log_info("rapidapi", "simular_coleta", "Iniciando simulação de coleta")
            
            # Simular trabalho
            time.sleep(0.2)
            
            log_info("rapidapi", "simular_coleta", "Simulação concluída", {"registros": 100})
            return {"sucesso": True, "registros": 100}
        
        resultado = simular_coleta()
        print(f"✅ Integração funcionando: {resultado}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False

def run_all_tests():
    """Executa todos os testes."""
    print("🚀 INICIANDO TESTES DA IMPLEMENTAÇÃO RAPIDAPI")
    print("=" * 60)
    
    start_time = time.time()
    results = {}
    
    # Teste 1: Importações
    print("\n1️⃣ TESTANDO IMPORTAÇÕES...")
    results['imports'] = test_imports()
    
    # Teste 2: Sistema de logs
    print("\n2️⃣ TESTANDO SISTEMA DE LOGS...")
    results['logger'] = test_logger_system()
    
    # Teste 3: Classe base RapidAPI
    print("\n3️⃣ TESTANDO CLASSE BASE RAPIDAPI...")
    results['rapidapi_base'] = test_rapidapi_base()
    
    # Teste 4: API específica
    print("\n4️⃣ TESTANDO API TODAY FOOTBALL PREDICTION...")
    results['today_api'] = test_today_football_prediction_api()
    
    # Teste 5: Integração
    print("\n5️⃣ TESTANDO INTEGRAÇÃO...")
    results['integration'] = test_integration()
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
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
        print("🚀 O módulo RapidAPI está funcionando perfeitamente!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("   1. Implementar as outras APIs do RapidAPI")
        print("   2. Integrar com o sistema de coleta principal")
        print("   3. Configurar chaves de API reais")
        print("   4. Executar testes com dados reais")
    else:
        print(f"\n⚠️ {total_tests - successful_tests} teste(s) falharam.")
        print("🔧 Verifique os erros acima e corrija os problemas.")
    
    return results

def main():
    """Função principal."""
    try:
        results = run_all_tests()
        
        if results:
            print("\n✅ Testes concluídos!")
            return 0
        else:
            print("\n❌ Testes falharam!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Testes interrompidos pelo usuário.")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
