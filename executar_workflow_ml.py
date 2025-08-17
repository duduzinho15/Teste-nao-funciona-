#!/usr/bin/env python3
"""
Script principal para executar o workflow completo de Machine Learning do ApostaPro.
Executa em sequência: preparação de dados, treinamento de modelos e geração de recomendações.

Use este script como ponto de entrada para execuções completas em ambiente de
produção. Para uma demonstração mais simples voltada a desenvolvimento ou
testes rápidos, utilize `demo_pipeline_ml.py`.
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow_ml.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def executar_preparacao_dados() -> bool:
    """
    Executa a preparação de dados para Machine Learning.
    
    Returns:
        True se executou com sucesso, False caso contrário
    """
    try:
        logger.info("🚀 INICIANDO FASE 1: PREPARAÇÃO DE DADOS")
        logger.info("=" * 60)
        
        # Importa e executa preparação de dados
        from ml_models.preparacao_dados import executar_preparacao_dados
        
        dataset = executar_preparacao_dados()
        
        if dataset is not None and not dataset.empty:
            logger.info("✅ PREPARAÇÃO DE DADOS CONCLUÍDA COM SUCESSO!")
            logger.info(f"📊 Dataset criado: {dataset.shape[0]} partidas, {dataset.shape[1]} features")
            return True
        else:
            logger.error("❌ FALHA NA PREPARAÇÃO DE DADOS")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERRO FATAL NA PREPARAÇÃO DE DADOS: {e}")
        return False

def executar_treinamento_modelos() -> bool:
    """
    Executa o treinamento dos modelos de Machine Learning.
    
    Returns:
        True se executou com sucesso, False caso contrário
    """
    try:
        logger.info("🤖 INICIANDO FASE 2: TREINAMENTO DE MODELOS")
        logger.info("=" * 60)
        
        # Verifica se o dataset existe
        if not os.path.exists('dataset_treinamento_ml.csv'):
            logger.error("❌ Dataset não encontrado. Execute a preparação de dados primeiro.")
            return False
        
        # Importa e executa treinamento
        from ml_models.treinamento import executar_treinamento_modelos
        
        resultados = executar_treinamento_modelos()
        
        if resultados:
            logger.info("✅ TREINAMENTO DE MODELOS CONCLUÍDO COM SUCESSO!")
            logger.info("📊 Modelos treinados:")
            for tipo, info in resultados.items():
                if info and 'melhor_modelo' in info:
                    logger.info(f"   • {tipo}: {info['melhor_modelo']}")
            return True
        else:
            logger.error("❌ FALHA NO TREINAMENTO DE MODELOS")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERRO FATAL NO TREINAMENTO: {e}")
        return False

def executar_geracao_recomendacoes() -> bool:
    """
    Executa a geração de recomendações usando os modelos treinados.
    
    Returns:
        True se executou com sucesso, False caso contrário
    """
    try:
        logger.info("🎯 INICIANDO FASE 3: GERAÇÃO DE RECOMENDAÇÕES")
        logger.info("=" * 60)
        
        # Verifica se os modelos foram treinados
        if not os.path.exists('modelos_treinados'):
            logger.error("❌ Diretório de modelos não encontrado. Execute o treinamento primeiro.")
            return False
        
        # Verifica se há arquivos de modelo
        arquivos_modelo = [f for f in os.listdir('modelos_treinados') if f.endswith('_modelo.pkl')]
        if not arquivos_modelo:
            logger.error("❌ Nenhum modelo encontrado. Execute o treinamento primeiro.")
            return False
        
        logger.info(f"📁 Modelos encontrados: {len(arquivos_modelo)}")
        for arquivo in arquivos_modelo:
            logger.info(f"   • {arquivo}")
        
        # Importa e executa geração de recomendações
        from ml_models.gerar_recomendacoes import executar_geracao_recomendacoes
        
        recomendacoes = executar_geracao_recomendacoes()
        
        if recomendacoes:
            logger.info("✅ GERAÇÃO DE RECOMENDAÇÕES CONCLUÍDA COM SUCESSO!")
            logger.info(f"🎯 {len(recomendacoes)} recomendações geradas")
            return True
        else:
            logger.warning("⚠️ Nenhuma recomendação foi gerada")
            return True  # Considera sucesso mesmo sem recomendações
            
    except Exception as e:
        logger.error(f"❌ ERRO FATAL NA GERAÇÃO DE RECOMENDAÇÕES: {e}")
        return False

def validar_api_recomendacoes() -> bool:
    """
    Valida se a API está funcionando e expondo as recomendações.
    
    Returns:
        True se a validação passou, False caso contrário
    """
    try:
        logger.info("🌐 INICIANDO FASE 4: VALIDAÇÃO DA API")
        logger.info("=" * 60)
        
        # Verifica se a API está rodando
        import requests
        import time
        
        # Aguarda um pouco para a API inicializar
        time.sleep(2)
        
        # Testa endpoint de saúde
        try:
            response = requests.get("http://localhost:8000/api/v1/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ API está respondendo")
            else:
                logger.error(f"❌ API retornou status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Não foi possível conectar com a API: {e}")
            logger.info("💡 Certifique-se de que a API está rodando em http://localhost:8000")
            return False
        
        # Testa endpoint de recomendações
        try:
            response = requests.get("http://localhost:8000/api/v1/recomendacoes/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Endpoint de recomendações funcionando: {data.get('total', 0)} recomendações")
                return True
            else:
                logger.error(f"❌ Endpoint de recomendações retornou status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao testar endpoint de recomendações: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERRO FATAL NA VALIDAÇÃO DA API: {e}")
        return False

def executar_workflow_completo() -> bool:
    """
    Executa o workflow completo de Machine Learning.
    
    Returns:
        True se todo o workflow foi executado com sucesso, False caso contrário
    """
    logger.info("🎯 INICIANDO WORKFLOW COMPLETO DE MACHINE LEARNING")
    logger.info("=" * 80)
    logger.info(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Fase 1: Preparação de dados
    if not executar_preparacao_dados():
        logger.error("❌ WORKFLOW INTERROMPIDO NA FASE 1")
        return False
    
    logger.info("✅ FASE 1 CONCLUÍDA - PREPARAÇÃO DE DADOS")
    logger.info("-" * 60)
    
    # Fase 2: Treinamento de modelos
    if not executar_treinamento_modelos():
        logger.error("❌ WORKFLOW INTERROMPIDO NA FASE 2")
        return False
    
    logger.info("✅ FASE 2 CONCLUÍDA - TREINAMENTO DE MODELOS")
    logger.info("-" * 60)
    
    # Fase 3: Geração de recomendações
    if not executar_geracao_recomendacoes():
        logger.error("❌ WORKFLOW INTERROMPIDO NA FASE 3")
        return False
    
    logger.info("✅ FASE 3 CONCLUÍDA - GERAÇÃO DE RECOMENDAÇÕES")
    logger.info("-" * 60)
    
    # Fase 4: Validação da API (opcional)
    logger.info("🌐 VALIDAÇÃO DA API (OPCIONAL)")
    if validar_api_recomendacoes():
        logger.info("✅ FASE 4 CONCLUÍDA - VALIDAÇÃO DA API")
    else:
        logger.warning("⚠️ FASE 4 - VALIDAÇÃO DA API FALHOU (mas não é crítica)")
    
    logger.info("=" * 80)
    logger.info("🎉 WORKFLOW COMPLETO EXECUTADO COM SUCESSO!")
    logger.info(f"⏰ Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    return True

def main():
    """
    Função principal do script.
    """
    try:
        # Verifica argumentos da linha de comando
        if len(sys.argv) > 1:
            comando = sys.argv[1].lower()
            
            if comando == "preparacao":
                logger.info("🎯 Executando apenas preparação de dados...")
                sucesso = executar_preparacao_dados()
            elif comando == "treinamento":
                logger.info("🎯 Executando apenas treinamento de modelos...")
                sucesso = executar_treinamento_modelos()
            elif comando == "recomendacoes":
                logger.info("🎯 Executando apenas geração de recomendações...")
                sucesso = executar_geracao_recomendacoes()
            elif comando == "validacao":
                logger.info("🎯 Executando apenas validação da API...")
                sucesso = validar_api_recomendacoes()
            elif comando == "help" or comando == "--help" or comando == "-h":
                mostrar_ajuda()
                return
            else:
                logger.error(f"❌ Comando inválido: {comando}")
                mostrar_ajuda()
                return
        else:
            # Executa workflow completo
            sucesso = executar_workflow_completo()
        
        # Resultado final
        if sucesso:
            logger.info("🎉 OPERAÇÃO EXECUTADA COM SUCESSO!")
            sys.exit(0)
        else:
            logger.error("❌ OPERAÇÃO FALHOU!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⚠️ Workflow interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ ERRO FATAL NO WORKFLOW: {e}")
        sys.exit(1)

def mostrar_ajuda():
    """
    Mostra a ajuda do script.
    """
    print("""
🎯 WORKFLOW DE MACHINE LEARNING - APOSTAPRO
===========================================

USO:
    python executar_workflow_ml.py [COMANDO]

COMANDOS:
    preparacao      - Executa apenas a preparação de dados
    treinamento     - Executa apenas o treinamento de modelos
    recomendacoes   - Executa apenas a geração de recomendações
    validacao       - Executa apenas a validação da API
    (sem comando)   - Executa o workflow completo

EXEMPLOS:
    python executar_workflow_ml.py                    # Workflow completo
    python executar_workflow_ml.py preparacao         # Apenas preparação
    python executar_workflow_ml.py treinamento        # Apenas treinamento
    python executar_workflow_ml.py recomendacoes      # Apenas recomendações
    python executar_workflow_ml.py validacao          # Apenas validação

PRÉ-REQUISITOS:
    • Banco de dados PostgreSQL configurado
    • Dependências Python instaladas (requirements.txt)
    • API rodando (opcional, para validação)

ARQUIVOS GERADOS:
    • dataset_treinamento_ml.csv          - Dataset preparado para ML
    • modelos_treinados/                   - Diretório com modelos treinados
    • workflow_ml.log                     - Log detalhado da execução
    • Recomendações salvas no banco de dados

LOG:
    O script gera logs detalhados em 'workflow_ml.log' e no console.
    """)

if __name__ == "__main__":
    main()
