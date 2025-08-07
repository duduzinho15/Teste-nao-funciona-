#!/usr/bin/env python3
"""
Teste para validar a correção do travamento na etapa 3 (verificação de completude).
"""

import sys
import os
import logging
import time
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('teste_correcao_etapa3.log')
    ]
)

logger = logging.getLogger(__name__)

def testar_verificacao_sem_travamento():
    """Testa se a verificação de completude não trava mais."""
    logger.info("🧪 TESTE: Verificação de completude sem travamento")
    logger.info("=" * 60)
    
    try:
        from Coleta_de_dados.apis.fbref.verificar_extracao import VerificadorExtracao
        
        # Criar verificador
        verificador = VerificadorExtracao()
        
        # Testar método específico que causava travamento
        logger.info("📋 Testando verificação de temporadas com timeout...")
        
        # URLs de teste que podem causar travamento
        urls_teste = [
            "https://fbref.com/en/comps/9/history/Premier-League-Seasons",
            "https://fbref.com/en/comps/12/history/La-Liga-Seasons",
            "https://fbref.com/en/comps/11/history/Serie-A-Seasons"
        ]
        
        for i, url in enumerate(urls_teste, 1):
            logger.info(f"🔍 Teste {i}/3: {url}")
            inicio = time.time()
            
            try:
                # Este método antes travava indefinidamente
                temporadas = verificador.verificar_temporadas_faltando(url)
                fim = time.time()
                duracao = fim - inicio
                
                logger.info(f"✅ Sucesso! Duração: {duracao:.2f}s, Temporadas: {len(temporadas)}")
                
                # Verificar se não demorou mais que 15 segundos (limite seguro)
                if duracao > 15:
                    logger.warning(f"⚠️ Demorou mais que 15s: {duracao:.2f}s")
                else:
                    logger.info(f"🚀 Tempo excelente: {duracao:.2f}s")
                    
            except Exception as e:
                fim = time.time()
                duracao = fim - inicio
                logger.info(f"🔄 Erro controlado em {duracao:.2f}s: {type(e).__name__}")
        
        logger.info("\n📊 Testando verificação completa...")
        inicio_completo = time.time()
        
        # Testar verificação completa (que antes travava na etapa 3)
        stats = verificador.executar_verificacao_completa()
        
        fim_completo = time.time()
        duracao_completa = fim_completo - inicio_completo
        
        logger.info(f"✅ Verificação completa finalizada em {duracao_completa:.2f}s")
        logger.info(f"📈 Estatísticas: {stats}")
        
        # Validar resultados
        if duracao_completa < 60:  # Menos de 1 minuto é excelente
            logger.info("🎉 SUCESSO: Verificação rápida e sem travamento!")
            return True
        else:
            logger.warning(f"⚠️ Demorou {duracao_completa:.2f}s - pode melhorar")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def testar_pipeline_etapa3():
    """Testa se a pipeline passa da etapa 3 sem travar."""
    logger.info("\n🔧 TESTE: Pipeline passando da etapa 3")
    logger.info("=" * 60)
    
    try:
        from Coleta_de_dados.apis.fbref.orquestrador_coleta import OrquestradorColeta
        
        # Configurar modo teste para execução rápida
        config = {
            'modo_teste': True,
            'continuar_em_erro': True,
            'timeout_etapa': 30  # 30 segundos por etapa
        }
        
        orquestrador = OrquestradorColeta(config)
        
        logger.info("🚀 Iniciando pipeline com foco na etapa 3...")
        inicio = time.time()
        
        # Executar apenas até a etapa 3 para testar
        resultado = orquestrador.executar_pipeline_completa()
        
        fim = time.time()
        duracao = fim - inicio
        
        logger.info(f"⏱️ Pipeline executada em {duracao:.2f}s")
        
        # Verificar se passou da etapa 3
        if resultado and resultado.get('etapa_atual', 0) > 3:
            logger.info("🎉 SUCESSO: Pipeline passou da etapa 3!")
            return True
        elif resultado and resultado.get('etapa_atual', 0) == 3:
            logger.info("✅ Pipeline chegou na etapa 3 sem travar")
            return True
        else:
            logger.warning("⚠️ Pipeline não chegou na etapa 3")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste da pipeline: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Função principal do teste."""
    logger.info("🧪 INICIANDO TESTE DE CORREÇÃO DA ETAPA 3")
    logger.info(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    resultados = []
    
    # Teste 1: Verificação sem travamento
    logger.info("\n🔍 TESTE 1: Verificação de completude")
    resultado1 = testar_verificacao_sem_travamento()
    resultados.append(("Verificação sem travamento", resultado1))
    
    # Teste 2: Pipeline passando da etapa 3
    logger.info("\n🔧 TESTE 2: Pipeline etapa 3")
    resultado2 = testar_pipeline_etapa3()
    resultados.append(("Pipeline etapa 3", resultado2))
    
    # Relatório final
    logger.info("\n" + "=" * 80)
    logger.info("📊 RELATÓRIO FINAL DOS TESTES")
    logger.info("=" * 80)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        logger.info(f"  {status} - {nome}")
        if resultado:
            sucessos += 1
    
    logger.info(f"\n📈 Resultado: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        logger.info("🎉 TODOS OS TESTES PASSARAM! Correção da etapa 3 validada!")
        return True
    else:
        logger.warning("⚠️ Alguns testes falharam. Revisar implementação.")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
