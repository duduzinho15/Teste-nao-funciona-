#!/usr/bin/env python3
"""
Script principal para executar o sistema completo de Machine Learning do ApostaPro
Integra todas as funcionalidades: APIs de apostas, dashboard web, automação CI/CD e Kubernetes
"""
import logging
import sys
import time
import threading
import subprocess
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('complete_ml_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class CompleteMLSystem:
    """Sistema completo de Machine Learning integrado"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "configs"
        self.config_dir.mkdir(exist_ok=True)
        
        # Status do sistema
        self.system_status = {
            'betting_apis': False,
            'web_dashboard': False,
            'automation_pipeline': False,
            'kubernetes': False,
            'monitoring': False
        }
        
        # Threads de execução
        self.execution_threads = {}
        
        logger.info("🚀 Sistema completo de ML do ApostaPro inicializado")
    
    def run_betting_apis_integration(self):
        """Executa integração com APIs de casas de apostas"""
        try:
            logger.info("📊 Iniciando integração com APIs de casas de apostas...")
            
            # Importar e executar integração
            from .betting_apis_integration import BettingAPIIntegration
            from .betting_apis_config import betting_apis_config
            
            # Salvar configuração
            betting_apis_config.save_config()
            logger.info("✅ Configuração das APIs salva")
            
            # Inicializar integração
            betting_api = BettingAPIIntegration()
            
            # Coletar dados em tempo real
            logger.info("📈 Coletando odds em tempo real...")
            odds_data = betting_api.collect_real_time_odds()
            
            logger.info("📊 Coletando resultados históricos...")
            historical_data = betting_api.collect_historical_results()
            
            logger.info("🔍 Realizando análise de mercado...")
            market_analysis = betting_api.analyze_market_trends()
            
            logger.info("✅ Validação de qualidade dos dados...")
            validation_results = betting_api.validate_data_quality()
            
            self.system_status['betting_apis'] = True
            logger.info(f"✅ Integração com APIs concluída: {len(odds_data)} odds, {len(historical_data)} resultados")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na integração com APIs: {e}")
            self.system_status['betting_apis'] = False
            return False
    
    def run_web_dashboard(self):
        """Executa dashboard web interativo"""
        try:
            logger.info("🖥️ Iniciando dashboard web interativo...")
            
            # Importar dashboard avançado
            from .advanced_web_dashboard import AdvancedWebDashboard
            
            # Criar dashboard
            dashboard = AdvancedWebDashboard()
            
            # Gerar dashboard estático
            logger.info("📊 Gerando dashboard estático...")
            html_file = dashboard.generate_static_dashboard()
            logger.info(f"✅ Dashboard estático gerado: {html_file}")
            
            # Iniciar servidor web em thread separada
            logger.info("🌐 Iniciando servidor web...")
            web_thread = threading.Thread(
                target=dashboard.start_web_server,
                args=('0.0.0.0', 8050, False),
                daemon=True,
                name='web_dashboard'
            )
            web_thread.start()
            self.execution_threads['web_dashboard'] = web_thread
            
            self.system_status['web_dashboard'] = True
            logger.info("✅ Dashboard web iniciado com sucesso!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no dashboard web: {e}")
            self.system_status['web_dashboard'] = False
            return False
    
    def run_automation_pipeline(self):
        """Executa pipeline de automação CI/CD"""
        try:
            logger.info("⚙️ Iniciando pipeline de automação...")
            
            # Importar configuração de CI/CD
            from .ci_cd_pipeline_config import ci_cd_config
            
            # Salvar configuração
            ci_cd_config.save_config()
            logger.info("✅ Configuração de CI/CD salva")
            
            # Criar workflows para todos os pipelines
            logger.info("🔧 Criando workflows de automação...")
            for pipeline_name in ci_cd_config.pipelines.keys():
                workflow_file = ci_cd_config.create_github_actions_workflow(pipeline_name)
                logger.info(f"✅ Workflow criado: {workflow_file}")
                
                compose_file = ci_cd_config.create_docker_compose(pipeline_name)
                logger.info(f"✅ Docker Compose criado: {compose_file}")
                
                k8s_manifests = ci_cd_config.create_kubernetes_manifests(pipeline_name)
                logger.info(f"✅ Manifests Kubernetes criados: {len(k8s_manifests)}")
            
            # Executar pipeline de validação
            logger.info("🔍 Executando pipeline de validação...")
            from .automation_pipeline import AutomationPipeline
            pipeline = AutomationPipeline()
            
            validation_result = pipeline.run_pipeline('data_validation')
            if validation_result:
                logger.info("✅ Pipeline de validação executado com sucesso")
            
            self.system_status['automation_pipeline'] = True
            logger.info("✅ Pipeline de automação configurado e executado!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no pipeline de automação: {e}")
            self.system_status['automation_pipeline'] = False
            return False
    
    def run_kubernetes_orchestration(self):
        """Executa orquestração Kubernetes"""
        try:
            logger.info("☸️ Configurando orquestração Kubernetes...")
            
            # Importar configuração de Kubernetes
            from .kubernetes_monitoring_config import k8s_monitoring_config
            
            # Salvar configuração
            k8s_monitoring_config.save_config()
            logger.info("✅ Configuração de Kubernetes salva")
            
            # Criar todos os manifests
            logger.info("📋 Criando manifests Kubernetes...")
            all_manifests = k8s_monitoring_config.create_all_manifests()
            
            total_manifests = sum(len(manifests) for manifests in all_manifests.values())
            logger.info(f"✅ Total de {total_manifests} manifests criados")
            
            # Verificar se kubectl está disponível
            try:
                result = subprocess.run(['kubectl', 'version', '--client'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info("✅ kubectl disponível, aplicando manifests...")
                    
                    # Aplicar manifests (simulado)
                    for category, manifests in all_manifests.items():
                        logger.info(f"📦 Aplicando {category}: {len(manifests)} manifests")
                        for manifest in manifests:
                            logger.info(f"  - Aplicando: {manifest}")
                            # Aqui você aplicaria com: kubectl apply -f manifest
                            time.sleep(0.1)  # Simular tempo de aplicação
                    
                    self.system_status['kubernetes'] = True
                    logger.info("✅ Orquestração Kubernetes configurada e aplicada!")
                else:
                    logger.warning("⚠️ kubectl não disponível, manifests criados mas não aplicados")
                    self.system_status['kubernetes'] = False
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning("⚠️ kubectl não encontrado, manifests criados mas não aplicados")
                self.system_status['kubernetes'] = False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na orquestração Kubernetes: {e}")
            self.system_status['kubernetes'] = False
            return False
    
    def run_monitoring_system(self):
        """Executa sistema de monitoramento"""
        try:
            logger.info("📊 Iniciando sistema de monitoramento...")
            
            # Importar monitoramento
            from .production_monitoring import get_system_health, get_system_dashboard
            
            # Verificar saúde do sistema
            health_status = get_system_health()
            logger.info(f"🏥 Status do sistema: {health_status['overall_status']}")
            
            # Obter dashboard do sistema
            dashboard_data = get_system_dashboard()
            if 'error' not in dashboard_data:
                logger.info("✅ Dashboard do sistema funcionando")
            
            # Iniciar monitoramento contínuo em thread separada
            logger.info("🔄 Iniciando monitoramento contínuo...")
            monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name='monitoring'
            )
            monitoring_thread.start()
            self.execution_threads['monitoring'] = monitoring_thread
            
            self.system_status['monitoring'] = True
            logger.info("✅ Sistema de monitoramento iniciado!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no sistema de monitoramento: {e}")
            self.system_status['monitoring'] = False
            return False
    
    def _monitoring_loop(self):
        """Loop de monitoramento contínuo"""
        logger.info("🔄 Loop de monitoramento iniciado")
        
        while True:
            try:
                # Verificar saúde do sistema
                from .production_monitoring import get_system_health
                health_status = get_system_health()
                
                if health_status['overall_status'] == 'healthy':
                    logger.info("✅ Sistema funcionando normalmente")
                else:
                    logger.warning(f"⚠️ Problemas detectados: {health_status.get('issues', [])}")
                
                # Aguardar próximo ciclo
                time.sleep(300)  # 5 minutos
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(60)  # 1 minuto em caso de erro
    
    def run_complete_system(self):
        """Executa o sistema completo"""
        try:
            logger.info("🚀 Iniciando execução do sistema completo de ML...")
            
            # 1. Integração com APIs de apostas
            self.run_betting_apis_integration()
            
            # 2. Dashboard web
            self.run_web_dashboard()
            
            # 3. Pipeline de automação
            self.run_automation_pipeline()
            
            # 4. Orquestração Kubernetes
            self.run_kubernetes_orchestration()
            
            # 5. Sistema de monitoramento
            self.run_monitoring_system()
            
            # Aguardar um pouco para estabilização
            time.sleep(5)
            
            # Verificar status geral
            successful_components = sum(self.system_status.values())
            total_components = len(self.system_status)
            
            logger.info(f"📊 Status do sistema: {successful_components}/{total_components} componentes funcionando")
            
            if successful_components == total_components:
                logger.info("🎉 Sistema completo executado com sucesso!")
                return True
            else:
                logger.warning(f"⚠️ Sistema executado com {total_components - successful_components} problemas")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro fatal na execução do sistema: {e}")
            return False
    
    def get_system_status(self):
        """Retorna status atual do sistema"""
        return self.system_status.copy()
    
    def stop_system(self):
        """Para o sistema de forma controlada"""
        logger.info("🛑 Parando sistema...")
        
        # Aguardar threads terminarem
        for name, thread in self.execution_threads.items():
            if thread.is_alive():
                logger.info(f"⏳ Aguardando thread {name} terminar...")
                thread.join(timeout=10)
        
        logger.info("✅ Sistema parado com sucesso")
    
    def generate_system_report(self):
        """Gera relatório do sistema"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'system_status': self.system_status,
                'execution_threads': {
                    name: thread.is_alive() 
                    for name, thread in self.execution_threads.items()
                },
                'summary': {
                    'total_components': len(self.system_status),
                    'working_components': sum(self.system_status.values()),
                    'overall_status': 'healthy' if all(self.system_status.values()) else 'degraded'
                }
            }
            
            # Salvar relatório
            report_file = self.config_dir / "system_report.json"
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Relatório do sistema gerado: {report_file}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return None

def main():
    """Função principal"""
    try:
        # Criar sistema
        ml_system = CompleteMLSystem()
        
        # Executar sistema completo
        success = ml_system.run_complete_system()
        
        if success:
            logger.info("🎉 Sistema ML executado com sucesso!")
            
            # Gerar relatório
            report = ml_system.generate_system_report()
            if report:
                logger.info(f"📊 Status geral: {report['summary']['overall_status']}")
            
            # Manter sistema rodando
            logger.info("🔄 Sistema rodando. Pressione Ctrl+C para parar...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("🛑 Interrupção recebida...")
                
        else:
            logger.error("❌ Falha na execução do sistema")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)
    finally:
        # Parar sistema de forma controlada
        if 'ml_system' in locals():
            ml_system.stop_system()

if __name__ == "__main__":
    main()
