#!/usr/bin/env python3
"""
Script principal para executar o pipeline completo de Machine Learning
Integra todas as funcionalidades: APIs de apostas, dashboard web, automação e Kubernetes
"""
import logging
import sys
import time
import threading
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_pipeline_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Função principal para executar o pipeline completo"""
    try:
        logger.info("🚀 Iniciando pipeline completo de Machine Learning do ApostaPro")
        
        # 1. INTEGRAÇÃO COM DADOS REAIS - APIs de casas de apostas
        logger.info("📊 Etapa 1: Integrando com APIs de casas de apostas...")
        execute_betting_apis_integration()
        
        # 2. INTERFACE WEB - Dashboard interativo
        logger.info("🖥️ Etapa 2: Iniciando dashboard web interativo...")
        execute_web_dashboard()
        
        # 3. AUTOMAÇÃO - Pipeline CI/CD
        logger.info("⚙️ Etapa 3: Executando pipeline de automação...")
        execute_automation_pipeline()
        
        # 4. ESCALABILIDADE - Kubernetes
        logger.info("☸️ Etapa 4: Configurando orquestração Kubernetes...")
        execute_kubernetes_orchestration()
        
        logger.info("✅ Pipeline completo executado com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro durante execução do pipeline: {e}")
        raise

def execute_betting_apis_integration():
    """Executa integração com APIs de casas de apostas"""
    try:
        from .betting_apis_integration import BettingAPIIntegration
        
        # Inicializar integração
        betting_api = BettingAPIIntegration()
        
        # Coletar odds em tempo real
        logger.info("📈 Coletando odds em tempo real...")
        odds_data = betting_api.collect_real_time_odds()
        
        # Coletar resultados históricos
        logger.info("📊 Coletando resultados históricos...")
        historical_data = betting_api.collect_historical_results()
        
        # Análise de mercado
        logger.info("🔍 Realizando análise de mercado...")
        market_analysis = betting_api.analyze_market_trends()
        
        # Validação de dados
        logger.info("✅ Validando qualidade dos dados...")
        validation_results = betting_api.validate_data_quality()
        
        logger.info(f"📊 Dados coletados: {len(odds_data)} odds, {len(historical_data)} resultados históricos")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na integração com APIs de apostas: {e}")
        return False

def execute_web_dashboard():
    """Executa dashboard web interativo"""
    try:
        from .web_dashboard import WebDashboard
        
        # Inicializar dashboard
        dashboard = WebDashboard()
        
        # Gerar gráficos principais
        logger.info("📊 Gerando gráficos do sistema...")
        system_chart = dashboard.generate_system_overview_chart()
        
        logger.info("📈 Gerando gráficos de performance...")
        performance_chart = dashboard.generate_performance_chart()
        
        logger.info("🎯 Gerando gráficos de apostas...")
        betting_chart = dashboard.generate_betting_analysis_chart()
        
        # Iniciar servidor web (em thread separada)
        logger.info("🌐 Iniciando servidor web...")
        web_thread = threading.Thread(target=dashboard.start_web_server, daemon=True)
        web_thread.start()
        
        logger.info("✅ Dashboard web iniciado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no dashboard web: {e}")
        return False

def execute_automation_pipeline():
    """Executa pipeline de automação CI/CD"""
    try:
        from .automation_pipeline import AutomationPipeline
        
        # Inicializar pipeline
        pipeline = AutomationPipeline()
        
        # Executar pipeline de treinamento
        logger.info("🤖 Executando pipeline de treinamento ML...")
        training_result = pipeline.run_pipeline('ml_training')
        
        # Executar pipeline de validação
        logger.info("🔍 Executando pipeline de validação...")
        validation_result = pipeline.run_pipeline('data_validation')
        
        # Executar pipeline de monitoramento
        logger.info("📊 Executando pipeline de monitoramento...")
        monitoring_result = pipeline.run_pipeline('performance_monitoring')
        
        # Verificar status dos pipelines
        pipeline_status = pipeline.get_pipeline_status()
        logger.info(f"📋 Status dos pipelines: {pipeline_status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no pipeline de automação: {e}")
        return False

def execute_kubernetes_orchestration():
    """Executa orquestração Kubernetes"""
    try:
        from .kubernetes_orchestration import KubernetesOrchestration
        
        # Inicializar orquestração
        k8s = KubernetesOrchestration()
        
        # Verificar conectividade
        logger.info("🔌 Verificando conectividade com Kubernetes...")
        if not k8s.check_cluster_connectivity():
            logger.warning("⚠️ Cluster Kubernetes não acessível, configurando localmente...")
            k8s.setup_local_environment()
        
        # Deploy dos serviços ML
        logger.info("🚀 Fazendo deploy dos serviços ML...")
        deployment_result = k8s.deploy_ml_services()
        
        # Configurar monitoramento
        logger.info("📊 Configurando monitoramento distribuído...")
        monitoring_result = k8s.setup_distributed_monitoring()
        
        # Configurar auto-scaling
        logger.info("📈 Configurando auto-scaling...")
        scaling_result = k8s.setup_auto_scaling()
        
        # Verificar status dos deployments
        deployment_status = k8s.get_deployment_status()
        logger.info(f"📋 Status dos deployments: {deployment_status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na orquestração Kubernetes: {e}")
        return False

def run_monitoring_loop():
    """Loop de monitoramento contínuo"""
    logger.info("🔄 Iniciando loop de monitoramento contínuo...")
    
    while True:
        try:
            # Verificar saúde do sistema
            from .production_monitoring import get_system_health
            health_status = get_system_health()
            
            if health_status['overall_status'] == 'healthy':
                logger.info("✅ Sistema funcionando normalmente")
            else:
                logger.warning(f"⚠️ Problemas detectados: {health_status['issues']}")
            
            # Aguardar próximo ciclo
            time.sleep(300)  # 5 minutos
            
        except Exception as e:
            logger.error(f"❌ Erro no monitoramento: {e}")
            time.sleep(60)  # 1 minuto em caso de erro

if __name__ == "__main__":
    try:
        # Executar pipeline principal
        main()
        
        # Iniciar monitoramento contínuo
        logger.info("🔄 Iniciando monitoramento contínuo...")
        monitoring_thread = threading.Thread(target=run_monitoring_loop, daemon=True)
        monitoring_thread.start()
        
        # Manter script rodando
        logger.info("🔄 Sistema rodando. Pressione Ctrl+C para parar...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Parando sistema...")
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)
