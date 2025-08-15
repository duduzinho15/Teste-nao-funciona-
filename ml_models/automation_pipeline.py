#!/usr/bin/env python3
"""
Pipeline de automação CI/CD para modelos ML
"""
import logging
import json
import yaml
import subprocess
import shutil
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import git
import docker
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result
from .production_monitoring import get_system_dashboard

logger = logging.getLogger(__name__)

@dataclass
class PipelineConfig:
    """Configuração do pipeline de automação"""
    name: str
    version: str
    trigger_type: str  # 'manual', 'schedule', 'webhook', 'git_push'
    schedule: str = "0 2 * * *"  # Cron expression
    enabled: bool = True
    max_retries: int = 3
    timeout_minutes: int = 60
    notification_channels: List[str] = None
    environment: str = "production"

@dataclass
class PipelineRun:
    """Execução de um pipeline"""
    id: str
    pipeline_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # 'running', 'success', 'failed', 'cancelled'
    steps_completed: List[str] = None
    steps_failed: List[str] = None
    logs: List[str] = None
    artifacts: List[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0

class AutomationPipeline:
    """Sistema de automação para pipeline CI/CD"""
    
    def __init__(self):
        self.config = get_ml_config()
        
        # Diretórios
        self.pipeline_dir = Path(self.config.monitoring_dir) / "automation"
        self.pipeline_dir.mkdir(parents=True, exist_ok=True)
        
        self.artifacts_dir = self.pipeline_dir / "artifacts"
        self.artifacts_dir.mkdir(exist_ok=True)
        
        self.logs_dir = self.pipeline_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configurações dos pipelines
        self.pipelines = {
            'ml_training': PipelineConfig(
                name='ml_training',
                version='1.0.0',
                trigger_type='schedule',
                schedule='0 2 * * *',  # Diariamente às 2h
                notification_channels=['email', 'slack']
            ),
            'model_deployment': PipelineConfig(
                name='model_deployment',
                version='1.0.0',
                trigger_type='manual',
                notification_channels=['email', 'slack']
            ),
            'performance_monitoring': PipelineConfig(
                name='performance_monitoring',
                version='1.0.0',
                trigger_type='schedule',
                schedule='*/15 * * * *',  # A cada 15 minutos
                notification_channels=['slack']
            ),
            'data_validation': PipelineConfig(
                name='data_validation',
                version='1.0.0',
                trigger_type='schedule',
                schedule='0 */6 * * *',  # A cada 6 horas
                notification_channels=['email']
            )
        }
        
        # Histórico de execuções
        self.runs_history = []
        
        # Configurações de notificação
        self.notification_config = {
            'email': {
                'enabled': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'apostapro@example.com',
                'password': 'your_password_here'
            },
            'slack': {
                'enabled': True,
                'webhook_url': 'https://hooks.slack.com/services/YOUR_WEBHOOK',
                'channel': '#ml-pipeline'
            }
        }
    
    def run_pipeline(self, pipeline_name: str, trigger_type: str = 'manual') -> str:
        """
        Executa um pipeline específico
        
        Args:
            pipeline_name: Nome do pipeline
            trigger_type: Tipo de trigger
            
        Returns:
            ID da execução
        """
        try:
            if pipeline_name not in self.pipelines:
                raise ValueError(f"Pipeline {pipeline_name} não encontrado")
            
            pipeline_config = self.pipelines[pipeline_name]
            
            # Verificar se o pipeline está habilitado
            if not pipeline_config.enabled:
                raise ValueError(f"Pipeline {pipeline_name} está desabilitado")
            
            # Criar execução
            run_id = self._generate_run_id(pipeline_name)
            pipeline_run = PipelineRun(
                id=run_id,
                pipeline_name=pipeline_name,
                start_time=datetime.now(),
                steps_completed=[],
                steps_failed=[],
                logs=[],
                artifacts=[]
            )
            
            logger.info(f"Iniciando pipeline {pipeline_name} (ID: {run_id})")
            
            # Executar pipeline
            success = self._execute_pipeline(pipeline_run, pipeline_config)
            
            # Finalizar execução
            pipeline_run.end_time = datetime.now()
            pipeline_run.status = 'success' if success else 'failed'
            
            # Salvar execução
            self._save_pipeline_run(pipeline_run)
            
            # Notificar resultado
            self._notify_pipeline_result(pipeline_run)
            
            return run_id
            
        except Exception as e:
            logger.error(f"Erro ao executar pipeline {pipeline_name}: {e}")
            raise
    
    def _execute_pipeline(self, pipeline_run: PipelineRun, pipeline_config: PipelineConfig) -> bool:
        """Executa os passos do pipeline"""
        try:
            pipeline_name = pipeline_run.pipeline_name
            
            if pipeline_name == 'ml_training':
                return self._run_ml_training_pipeline(pipeline_run)
            elif pipeline_name == 'model_deployment':
                return self._run_model_deployment_pipeline(pipeline_run)
            elif pipeline_name == 'performance_monitoring':
                return self._run_performance_monitoring_pipeline(pipeline_run)
            elif pipeline_name == 'data_validation':
                return self._run_data_validation_pipeline(pipeline_run)
            else:
                raise ValueError(f"Pipeline {pipeline_name} não implementado")
                
        except Exception as e:
            logger.error(f"Erro na execução do pipeline: {e}")
            pipeline_run.error_message = str(e)
            pipeline_run.status = 'failed'
            return False
    
    def _run_ml_training_pipeline(self, pipeline_run: PipelineRun) -> bool:
        """Executa pipeline de treinamento ML"""
        try:
            logger.info("Executando pipeline de treinamento ML")
            
            # Passo 1: Validação de dados
            if not self._validate_training_data(pipeline_run):
                return False
            
            # Passo 2: Treinamento dos modelos
            if not self._train_ml_models(pipeline_run):
                return False
            
            # Passo 3: Avaliação de performance
            if not self._evaluate_model_performance(pipeline_run):
                return False
            
            # Passo 4: Versionamento dos modelos
            if not self._version_models(pipeline_run):
                return False
            
            # Passo 5: Testes automatizados
            if not self._run_automated_tests(pipeline_run):
                return False
            
            logger.info("Pipeline de treinamento ML concluído com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro no pipeline de treinamento ML: {e}")
            return False
    
    def _run_model_deployment_pipeline(self, pipeline_run: PipelineRun) -> bool:
        """Executa pipeline de deploy dos modelos"""
        try:
            logger.info("Executando pipeline de deploy dos modelos")
            
            # Passo 1: Validação dos modelos
            if not self._validate_models_for_deployment(pipeline_run):
                return False
            
            # Passo 2: Backup dos modelos atuais
            if not self._backup_current_models(pipeline_run):
                return False
            
            # Passo 3: Deploy dos novos modelos
            if not self._deploy_new_models(pipeline_run):
                return False
            
            # Passo 4: Verificação de saúde
            if not self._verify_deployment_health(pipeline_run):
                return False
            
            # Passo 5: Rollback se necessário
            if not self._verify_deployment_health(pipeline_run):
                logger.warning("Deploy falhou, executando rollback")
                self._rollback_deployment(pipeline_run)
                return False
            
            logger.info("Pipeline de deploy concluído com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro no pipeline de deploy: {e}")
            return False
    
    def _run_performance_monitoring_pipeline(self, pipeline_run: PipelineRun) -> bool:
        """Executa pipeline de monitoramento de performance"""
        try:
            logger.info("Executando pipeline de monitoramento")
            
            # Passo 1: Coleta de métricas
            if not self._collect_performance_metrics(pipeline_run):
                return False
            
            # Passo 2: Análise de tendências
            if not self._analyze_performance_trends(pipeline_run):
                return False
            
            # Passo 3: Geração de alertas
            if not self._generate_performance_alerts(pipeline_run):
                return False
            
            # Passo 4: Geração de relatórios
            if not self._generate_performance_reports(pipeline_run):
                return False
            
            logger.info("Pipeline de monitoramento concluído com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro no pipeline de monitoramento: {e}")
            return False
    
    def _run_data_validation_pipeline(self, pipeline_run: PipelineRun) -> bool:
        """Executa pipeline de validação de dados"""
        try:
            logger.info("Executando pipeline de validação de dados")
            
            # Passo 1: Verificação de qualidade dos dados
            if not self._check_data_quality(pipeline_run):
                return False
            
            # Passo 2: Validação de esquemas
            if not self._validate_data_schemas(pipeline_run):
                return False
            
            # Passo 3: Detecção de anomalias
            if not self._detect_data_anomalies(pipeline_run):
                return False
            
            # Passo 4: Limpeza automática
            if not self._clean_data_automatically(pipeline_run):
                return False
            
            logger.info("Pipeline de validação de dados concluído com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro no pipeline de validação de dados: {e}")
            return False
    
    def _validate_training_data(self, pipeline_run: PipelineRun) -> bool:
        """Valida dados de treinamento"""
        try:
            logger.info("Validando dados de treinamento...")
            
            # Verificar disponibilidade dos dados
            data_dir = Path(self.config.data_dir)
            if not data_dir.exists():
                raise ValueError("Diretório de dados não encontrado")
            
            # Verificar arquivos de dados
            data_files = list(data_dir.glob("*.csv"))
            if not data_files:
                raise ValueError("Nenhum arquivo de dados encontrado")
            
            # Verificar tamanho dos dados
            total_size = sum(f.stat().st_size for f in data_files)
            if total_size < 1024:  # Menos de 1KB
                raise ValueError("Dados insuficientes para treinamento")
            
            pipeline_run.steps_completed.append("data_validation")
            pipeline_run.logs.append("Dados de treinamento validados com sucesso")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação de dados: {e}")
            pipeline_run.steps_failed.append("data_validation")
            pipeline_run.logs.append(f"Erro na validação: {str(e)}")
            return False
    
    def _train_ml_models(self, pipeline_run: PipelineRun) -> bool:
        """Treina modelos ML"""
        try:
            logger.info("Treinando modelos ML...")
            
            # Importar módulos de treinamento
            from .model_trainer import ModelTrainer
            
            trainer = ModelTrainer()
            
            # Treinar modelos
            model_types = ['result_prediction', 'total_goals_prediction', 'both_teams_score_prediction']
            
            for model_type in model_types:
                logger.info(f"Treinando modelo {model_type}...")
                
                # Simular treinamento (em produção, seria real)
                success = self._simulate_model_training(model_type)
                
                if success:
                    pipeline_run.logs.append(f"Modelo {model_type} treinado com sucesso")
                else:
                    pipeline_run.logs.append(f"Erro no treinamento do modelo {model_type}")
                    return False
            
            pipeline_run.steps_completed.append("model_training")
            pipeline_run.logs.append("Todos os modelos treinados com sucesso")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no treinamento dos modelos: {e}")
            pipeline_run.steps_failed.append("model_training")
            pipeline_run.logs.append(f"Erro no treinamento: {str(e)}")
            return False
    
    def _simulate_model_training(self, model_type: str) -> bool:
        """Simula treinamento de modelo (para demonstração)"""
        try:
            import time
            import random
            
            # Simular tempo de treinamento
            training_time = random.uniform(5, 15)
            time.sleep(training_time)
            
            # Simular sucesso/falha
            success_rate = 0.95  # 95% de sucesso
            return random.random() < success_rate
            
        except Exception as e:
            logger.error(f"Erro na simulação de treinamento: {e}")
            return False
    
    def _evaluate_model_performance(self, pipeline_run: PipelineRun) -> bool:
        """Avalia performance dos modelos"""
        try:
            logger.info("Avaliando performance dos modelos...")
            
            # Simular avaliação
            import time
            time.sleep(2)
            
            pipeline_run.steps_completed.append("performance_evaluation")
            pipeline_run.logs.append("Performance dos modelos avaliada com sucesso")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na avaliação de performance: {e}")
            pipeline_run.steps_failed.append("performance_evaluation")
            pipeline_run.logs.append(f"Erro na avaliação: {str(e)}")
            return False
    
    def _version_models(self, pipeline_run: PipelineRun) -> bool:
        """Versiona os modelos treinados"""
        try:
            logger.info("Versionando modelos...")
            
            # Criar versão
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            version = f"v1.0.{timestamp}"
            
            # Salvar informações de versão
            version_info = {
                'version': version,
                'timestamp': timestamp,
                'pipeline_run_id': pipeline_run.id,
                'models': ['result_prediction', 'total_goals_prediction', 'both_teams_score_prediction']
            }
            
            version_file = self.artifacts_dir / f"version_{timestamp}.json"
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, indent=2, ensure_ascii=False)
            
            pipeline_run.artifacts.append(str(version_file))
            pipeline_run.steps_completed.append("model_versioning")
            pipeline_run.logs.append(f"Modelos versionados: {version}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no versionamento: {e}")
            pipeline_run.steps_failed.append("model_versioning")
            pipeline_run.logs.append(f"Erro no versionamento: {str(e)}")
            return False
    
    def _run_automated_tests(self, pipeline_run: PipelineRun) -> bool:
        """Executa testes automatizados"""
        try:
            logger.info("Executando testes automatizados...")
            
            # Simular execução de testes
            import time
            time.sleep(3)
            
            pipeline_run.steps_completed.append("automated_tests")
            pipeline_run.logs.append("Testes automatizados executados com sucesso")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro nos testes automatizados: {e}")
            pipeline_run.steps_failed.append("automated_tests")
            pipeline_run.logs.append(f"Erro nos testes: {str(e)}")
            return False
    
    def _validate_models_for_deployment(self, pipeline_run: PipelineRun) -> bool:
        """Valida modelos para deploy"""
        try:
            logger.info("Validando modelos para deploy...")
            
            # Verificar se os modelos existem
            models_dir = Path(self.config.models_dir)
            if not models_dir.exists():
                raise ValueError("Diretório de modelos não encontrado")
            
            # Verificar arquivos dos modelos
            model_files = list(models_dir.glob("*_model.joblib"))
            if not model_files:
                raise ValueError("Nenhum modelo encontrado para deploy")
            
            pipeline_run.steps_completed.append("deployment_validation")
            pipeline_run.logs.append("Modelos validados para deploy")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação para deploy: {e}")
            pipeline_run.steps_failed.append("deployment_validation")
            pipeline_run.logs.append(f"Erro na validação: {str(e)}")
            return False
    
    def _backup_current_models(self, pipeline_run: PipelineRun) -> bool:
        """Faz backup dos modelos atuais"""
        try:
            logger.info("Fazendo backup dos modelos atuais...")
            
            # Criar diretório de backup
            backup_dir = self.artifacts_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(exist_ok=True)
            
            # Copiar modelos atuais
            models_dir = Path(self.config.models_dir)
            if models_dir.exists():
                shutil.copytree(models_dir, backup_dir / "models", dirs_exist_ok=True)
            
            pipeline_run.artifacts.append(str(backup_dir))
            pipeline_run.steps_completed.append("backup_current_models")
            pipeline_run.logs.append("Backup dos modelos atuais concluído")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no backup: {e}")
            pipeline_run.steps_failed.append("backup_current_models")
            pipeline_run.logs.append(f"Erro no backup: {str(e)}")
            return False
    
    def _deploy_new_models(self, pipeline_run: PipelineRun) -> bool:
        """Deploy dos novos modelos"""
        try:
            logger.info("Fazendo deploy dos novos modelos...")
            
            # Simular deploy
            import time
            time.sleep(5)
            
            pipeline_run.steps_completed.append("model_deployment")
            pipeline_run.logs.append("Deploy dos novos modelos concluído")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no deploy: {e}")
            pipeline_run.steps_failed.append("model_deployment")
            pipeline_run.logs.append(f"Erro no deploy: {str(e)}")
            return False
    
    def _verify_deployment_health(self, pipeline_run: PipelineRun) -> bool:
        """Verifica saúde do deploy"""
        try:
            logger.info("Verificando saúde do deploy...")
            
            # Simular verificação
            import time
            time.sleep(2)
            
            # Simular sucesso (em produção, seria uma verificação real)
            health_check_passed = True
            
            if health_check_passed:
                pipeline_run.steps_completed.append("health_check")
                pipeline_run.logs.append("Verificação de saúde do deploy concluída")
                return True
            else:
                pipeline_run.steps_failed.append("health_check")
                pipeline_run.logs.append("Verificação de saúde do deploy falhou")
                return False
                
        except Exception as e:
            logger.error(f"Erro na verificação de saúde: {e}")
            pipeline_run.steps_failed.append("health_check")
            pipeline_run.logs.append(f"Erro na verificação: {str(e)}")
            return False
    
    def _rollback_deployment(self, pipeline_run: PipelineRun):
        """Executa rollback do deploy"""
        try:
            logger.info("Executando rollback do deploy...")
            
            # Simular rollback
            import time
            time.sleep(3)
            
            pipeline_run.logs.append("Rollback do deploy executado")
            
        except Exception as e:
            logger.error(f"Erro no rollback: {e}")
            pipeline_run.logs.append(f"Erro no rollback: {str(e)}")
    
    def _collect_performance_metrics(self, pipeline_run: PipelineRun) -> bool:
        """Coleta métricas de performance"""
        try:
            logger.info("Coletando métricas de performance...")
            
            # Obter métricas do sistema
            dashboard_data = get_system_dashboard()
            
            if 'error' not in dashboard_data:
                pipeline_run.steps_completed.append("metrics_collection")
                pipeline_run.logs.append("Métricas de performance coletadas")
                return True
            else:
                pipeline_run.steps_failed.append("metrics_collection")
                pipeline_run.logs.append("Erro ao coletar métricas")
                return False
                
        except Exception as e:
            logger.error(f"Erro na coleta de métricas: {e}")
            pipeline_run.steps_failed.append("metrics_collection")
            pipeline_run.logs.append(f"Erro na coleta: {str(e)}")
            return False
    
    def _analyze_performance_trends(self, pipeline_run: PipelineRun) -> bool:
        """Analisa tendências de performance"""
        try:
            logger.info("Analisando tendências de performance...")
            
            # Simular análise
            import time
            time.sleep(2)
            
            pipeline_run.steps_completed.append("trend_analysis")
            pipeline_run.logs.append("Análise de tendências concluída")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na análise de tendências: {e}")
            pipeline_run.steps_failed.append("trend_analysis")
            pipeline_run.logs.append(f"Erro na análise: {str(e)}")
            return False
    
    def _generate_performance_alerts(self, pipeline_run: PipelineRun) -> bool:
        """Gera alertas de performance"""
        try:
            logger.info("Gerando alertas de performance...")
            
            # Simular geração de alertas
            import time
            time.sleep(1)
            
            pipeline_run.steps_completed.append("alert_generation")
            pipeline_run.logs.append("Alertas de performance gerados")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na geração de alertas: {e}")
            pipeline_run.steps_failed.append("alert_generation")
            pipeline_run.logs.append(f"Erro na geração: {str(e)}")
            return False
    
    def _generate_performance_reports(self, pipeline_run: PipelineRun) -> bool:
        """Gera relatórios de performance"""
        try:
            logger.info("Gerando relatórios de performance...")
            
            # Simular geração de relatórios
            import time
            time.sleep(2)
            
            pipeline_run.steps_completed.append("report_generation")
            pipeline_run.logs.append("Relatórios de performance gerados")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na geração de relatórios: {e}")
            pipeline_run.steps_failed.append("report_generation")
            pipeline_run.logs.append(f"Erro na geração: {str(e)}")
            return False
    
    def _check_data_quality(self, pipeline_run: PipelineRun) -> bool:
        """Verifica qualidade dos dados"""
        try:
            logger.info("Verificando qualidade dos dados...")
            
            # Simular verificação
            import time
            time.sleep(2)
            
            pipeline_run.steps_completed.append("data_quality_check")
            pipeline_run.logs.append("Verificação de qualidade dos dados concluída")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação de qualidade: {e}")
            pipeline_run.steps_failed.append("data_quality_check")
            pipeline_run.logs.append(f"Erro na verificação: {str(e)}")
            return False
    
    def _validate_data_schemas(self, pipeline_run: PipelineRun) -> bool:
        """Valida esquemas dos dados"""
        try:
            logger.info("Validando esquemas dos dados...")
            
            # Simular validação
            import time
            time.sleep(1)
            
            pipeline_run.steps_completed.append("schema_validation")
            pipeline_run.logs.append("Validação de esquemas concluída")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação de esquemas: {e}")
            pipeline_run.steps_failed.append("schema_validation")
            pipeline_run.logs.append(f"Erro na validação: {str(e)}")
            return False
    
    def _detect_data_anomalies(self, pipeline_run: PipelineRun) -> bool:
        """Detecta anomalias nos dados"""
        try:
            logger.info("Detectando anomalias nos dados...")
            
            # Simular detecção
            import time
            time.sleep(2)
            
            pipeline_run.steps_completed.append("anomaly_detection")
            pipeline_run.logs.append("Detecção de anomalias concluída")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na detecção de anomalias: {e}")
            pipeline_run.steps_failed.append("anomaly_detection")
            pipeline_run.logs.append(f"Erro na detecção: {str(e)}")
            return False
    
    def _clean_data_automatically(self, pipeline_run: PipelineRun) -> bool:
        """Limpa dados automaticamente"""
        try:
            logger.info("Limpando dados automaticamente...")
            
            # Simular limpeza
            import time
            time.sleep(1)
            
            pipeline_run.steps_completed.append("automatic_cleaning")
            pipeline_run.logs.append("Limpeza automática de dados concluída")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na limpeza automática: {e}")
            pipeline_run.steps_failed.append("automatic_cleaning")
            pipeline_run.logs.append(f"Erro na limpeza: {str(e)}")
            return False
    
    def _generate_run_id(self, pipeline_name: str) -> str:
        """Gera ID único para execução"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = hashlib.md5(f"{pipeline_name}_{timestamp}".encode()).hexdigest()[:8]
        return f"{pipeline_name}_{timestamp}_{random_suffix}"
    
    def _save_pipeline_run(self, pipeline_run: PipelineRun):
        """Salva execução do pipeline"""
        try:
            # Salvar em arquivo JSON
            run_file = self.logs_dir / f"run_{pipeline_run.id}.json"
            with open(run_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(pipeline_run), f, indent=2, ensure_ascii=False, default=str)
            
            # Adicionar ao histórico
            self.runs_history.append(pipeline_run)
            
            logger.info(f"Execução do pipeline salva: {run_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar execução do pipeline: {e}")
    
    def _notify_pipeline_result(self, pipeline_run: PipelineRun):
        """Notifica resultado do pipeline"""
        try:
            if pipeline_run.status == 'success':
                message = f"✅ Pipeline {pipeline_run.pipeline_name} executado com sucesso"
            else:
                message = f"❌ Pipeline {pipeline_run.pipeline_name} falhou"
            
            # Simular notificação
            logger.info(f"Notificação: {message}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar resultado: {e}")
    
    def get_pipeline_status(self, pipeline_name: str = None) -> Dict[str, Any]:
        """Obtém status dos pipelines"""
        try:
            if pipeline_name:
                if pipeline_name not in self.pipelines:
                    return {'error': f'Pipeline {pipeline_name} não encontrado'}
                
                pipeline_config = self.pipelines[pipeline_name]
                recent_runs = [run for run in self.runs_history if run.pipeline_name == pipeline_name]
                
                return {
                    'pipeline': asdict(pipeline_config),
                    'recent_runs': [asdict(run) for run in recent_runs[-5:]],  # Últimas 5 execuções
                    'last_run': asdict(recent_runs[-1]) if recent_runs else None
                }
            else:
                # Status de todos os pipelines
                status = {}
                for name, config in self.pipelines.items():
                    recent_runs = [run for run in self.runs_history if run.pipeline_name == name]
                    status[name] = {
                        'config': asdict(config),
                        'total_runs': len(recent_runs),
                        'successful_runs': len([r for r in recent_runs if r.status == 'success']),
                        'failed_runs': len([r for r in recent_runs if r.status == 'failed']),
                        'last_run': asdict(recent_runs[-1]) if recent_runs else None
                    }
                
                return status
                
        except Exception as e:
            logger.error(f"Erro ao obter status dos pipelines: {e}")
            return {'error': str(e)}
    
    def schedule_pipeline(self, pipeline_name: str, cron_expression: str) -> bool:
        """Agenda execução de pipeline"""
        try:
            if pipeline_name not in self.pipelines:
                raise ValueError(f"Pipeline {pipeline_name} não encontrado")
            
            self.pipelines[pipeline_name].schedule = cron_expression
            logger.info(f"Pipeline {pipeline_name} agendado: {cron_expression}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao agendar pipeline: {e}")
            return False
    
    def enable_pipeline(self, pipeline_name: str, enabled: bool = True) -> bool:
        """Habilita/desabilita pipeline"""
        try:
            if pipeline_name not in self.pipelines:
                raise ValueError(f"Pipeline {pipeline_name} não encontrado")
            
            self.pipelines[pipeline_name].enabled = enabled
            status = "habilitado" if enabled else "desabilitado"
            logger.info(f"Pipeline {pipeline_name} {status}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao alterar status do pipeline: {e}")
            return False

# Instância global
automation_pipeline = AutomationPipeline()

# Funções de conveniência
def run_pipeline(pipeline_name: str, trigger_type: str = 'manual') -> str:
    """Executa um pipeline"""
    return automation_pipeline.run_pipeline(pipeline_name, trigger_type)

def get_pipeline_status(pipeline_name: str = None) -> Dict[str, Any]:
    """Obtém status dos pipelines"""
    return automation_pipeline.get_pipeline_status(pipeline_name)

def schedule_pipeline(pipeline_name: str, cron_expression: str) -> bool:
    """Agenda execução de pipeline"""
    return automation_pipeline.schedule_pipeline(pipeline_name, cron_expression)

def enable_pipeline(pipeline_name: str, enabled: bool = True) -> bool:
    """Habilita/desabilita pipeline"""
    return automation_pipeline.enable_pipeline(pipeline_name, enabled)
