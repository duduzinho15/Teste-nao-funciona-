#!/usr/bin/env python3
"""
Configuração do pipeline de CI/CD para automação de modelos ML
"""
import os
import yaml
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta

@dataclass
class PipelineStage:
    """Estágio de um pipeline"""
    name: str
    description: str
    commands: List[str]
    timeout_minutes: int = 30
    retry_count: int = 2
    required: bool = True
    parallel: bool = False
    dependencies: List[str] = None

@dataclass
class PipelineConfig:
    """Configuração completa de um pipeline"""
    name: str
    version: str
    description: str
    trigger_type: str  # 'manual', 'schedule', 'webhook', 'git_push'
    schedule: str = "0 2 * * *"  # Cron expression
    enabled: bool = True
    stages: List[PipelineStage] = None
    environment: str = "production"
    notification_channels: List[str] = None
    artifacts: List[str] = None
    cache: Dict[str, Any] = None

class CICDPipelineConfig:
    """Configuração centralizada para pipelines de CI/CD"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "configs"
        self.config_dir.mkdir(exist_ok=True)
        
        # Pipelines principais
        self.pipelines = {
            'ml_training': PipelineConfig(
                name='ml_training',
                version='1.0.0',
                description='Pipeline de treinamento de modelos ML',
                trigger_type='schedule',
                schedule='0 2 * * *',  # Diariamente às 2h
                environment='production',
                notification_channels=['email', 'slack'],
                artifacts=['models', 'metrics', 'logs'],
                stages=[
                    PipelineStage(
                        name='data_preparation',
                        description='Preparação e validação dos dados',
                        commands=[
                            'python -m ml_models.data_preparation',
                            'python -m ml_models.data_validation'
                        ],
                        timeout_minutes=45
                    ),
                    PipelineStage(
                        name='feature_engineering',
                        description='Engenharia de features',
                        commands=[
                            'python -m ml_models.advanced_features',
                            'python -m ml_models.feature_selection'
                        ],
                        timeout_minutes=30
                    ),
                    PipelineStage(
                        name='model_training',
                        description='Treinamento dos modelos',
                        commands=[
                            'python -m ml_models.model_trainer',
                            'python -m ml_models.hyperparameter_tuning'
                        ],
                        timeout_minutes=120
                    ),
                    PipelineStage(
                        name='model_evaluation',
                        description='Avaliação e validação dos modelos',
                        commands=[
                            'python -m ml_models.model_evaluation',
                            'python -m ml_models.cross_validation'
                        ],
                        timeout_minutes=60
                    ),
                    PipelineStage(
                        name='model_deployment',
                        description='Deploy dos modelos em produção',
                        commands=[
                            'python -m ml_models.model_deployment',
                            'python -m ml_models.health_check'
                        ],
                        timeout_minutes=30
                    )
                ]
            ),
            
            'data_validation': PipelineConfig(
                name='data_validation',
                version='1.0.0',
                description='Pipeline de validação de dados',
                trigger_type='schedule',
                schedule='0 */6 * * *',  # A cada 6 horas
                environment='production',
                notification_channels=['email'],
                artifacts=['validation_reports', 'data_quality_metrics'],
                stages=[
                    PipelineStage(
                        name='data_collection',
                        description='Coleta de dados das APIs',
                        commands=[
                            'python -m ml_models.data_collector',
                            'python -m ml_models.betting_apis_integration'
                        ],
                        timeout_minutes=30
                    ),
                    PipelineStage(
                        name='data_validation',
                        description='Validação de qualidade dos dados',
                        commands=[
                            'python -m ml_models.data_validation',
                            'python -m ml_models.outlier_detection'
                        ],
                        timeout_minutes=45
                    ),
                    PipelineStage(
                        name='data_cleaning',
                        description='Limpeza e normalização dos dados',
                        commands=[
                            'python -m ml_models.data_cleaning',
                            'python -m ml_models.data_normalization'
                        ],
                        timeout_minutes=30
                    )
                ]
            ),
            
            'performance_monitoring': PipelineConfig(
                name='performance_monitoring',
                version='1.0.0',
                description='Pipeline de monitoramento de performance',
                trigger_type='schedule',
                schedule='*/15 * * * *',  # A cada 15 minutos
                environment='production',
                notification_channels=['slack'],
                artifacts=['performance_reports', 'alert_logs'],
                stages=[
                    PipelineStage(
                        name='metrics_collection',
                        description='Coleta de métricas do sistema',
                        commands=[
                            'python -m ml_models.production_monitoring',
                            'python -m ml_models.performance_metrics'
                        ],
                        timeout_minutes=15
                    ),
                    PipelineStage(
                        name='performance_analysis',
                        description='Análise de performance',
                        commands=[
                            'python -m ml_models.performance_analysis',
                            'python -m ml_models.anomaly_detection'
                        ],
                        timeout_minutes=20
                    ),
                    PipelineStage(
                        name='alert_generation',
                        description='Geração de alertas',
                        commands=[
                            'python -m ml_models.alert_system',
                            'python -m ml_models.notification_service'
                        ],
                        timeout_minutes=10
                    )
                ]
            ),
            
            'model_deployment': PipelineConfig(
                name='model_deployment',
                version='1.0.0',
                description='Pipeline de deploy de modelos',
                trigger_type='manual',
                environment='production',
                notification_channels=['email', 'slack'],
                artifacts=['deployment_logs', 'rollback_scripts'],
                stages=[
                    PipelineStage(
                        name='pre_deployment_check',
                        description='Verificações pré-deploy',
                        commands=[
                            'python -m ml_models.pre_deployment_check',
                            'python -m ml_models.model_compatibility_test'
                        ],
                        timeout_minutes=20
                    ),
                    PipelineStage(
                        name='deployment',
                        description='Deploy do modelo',
                        commands=[
                            'python -m ml_models.model_deployment',
                            'python -m ml_models.load_balancer_update'
                        ],
                        timeout_minutes=30
                    ),
                    PipelineStage(
                        name='post_deployment_validation',
                        description='Validação pós-deploy',
                        commands=[
                            'python -m ml_models.post_deployment_test',
                            'python -m ml_models.performance_validation'
                        ],
                        timeout_minutes=25
                    )
                ]
            )
        }
        
        # Configurações de ambiente
        self.environments = {
            'development': {
                'name': 'Development',
                'description': 'Ambiente de desenvolvimento',
                'variables': {
                    'ML_ENV': 'development',
                    'DEBUG': 'true',
                    'LOG_LEVEL': 'DEBUG'
                }
            },
            'staging': {
                'name': 'Staging',
                'description': 'Ambiente de homologação',
                'variables': {
                    'ML_ENV': 'staging',
                    'DEBUG': 'false',
                    'LOG_LEVEL': 'INFO'
                }
            },
            'production': {
                'name': 'Production',
                'description': 'Ambiente de produção',
                'variables': {
                    'ML_ENV': 'production',
                    'DEBUG': 'false',
                    'LOG_LEVEL': 'WARNING'
                }
            }
        }
        
        # Configurações de notificação
        self.notification_config = {
            'email': {
                'enabled': True,
                'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'username': os.getenv('SMTP_USERNAME', ''),
                'password': os.getenv('SMTP_PASSWORD', ''),
                'recipients': os.getenv('NOTIFICATION_EMAILS', '').split(',')
            },
            'slack': {
                'enabled': True,
                'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
                'channel': os.getenv('SLACK_CHANNEL', '#ml-pipeline'),
                'username': 'ApostaPro ML Pipeline'
            }
        }
        
        # Configurações de cache
        self.cache_config = {
            'enabled': True,
            'type': 'redis',  # 'redis', 'memory', 'file'
            'redis_host': os.getenv('REDIS_HOST', 'localhost'),
            'redis_port': int(os.getenv('REDIS_PORT', '6379')),
            'redis_db': int(os.getenv('REDIS_DB', '0')),
            'ttl': 3600,  # 1 hora
            'max_size': 1000
        }
    
    def get_pipeline_config(self, pipeline_name: str) -> Optional[PipelineConfig]:
        """Obtém configuração de um pipeline específico"""
        return self.pipelines.get(pipeline_name)
    
    def get_enabled_pipelines(self) -> Dict[str, PipelineConfig]:
        """Obtém apenas os pipelines habilitados"""
        return {name: config for name, config in self.pipelines.items() if config.enabled}
    
    def get_pipeline_stages(self, pipeline_name: str) -> List[PipelineStage]:
        """Obtém estágios de um pipeline específico"""
        pipeline = self.get_pipeline_config(pipeline_name)
        return pipeline.stages if pipeline else []
    
    def get_environment_variables(self, environment: str) -> Dict[str, str]:
        """Obtém variáveis de ambiente para um ambiente específico"""
        env_config = self.environments.get(environment, {})
        return env_config.get('variables', {})
    
    def create_github_actions_workflow(self, pipeline_name: str) -> str:
        """Cria workflow do GitHub Actions para um pipeline"""
        pipeline = self.get_pipeline_config(pipeline_name)
        if not pipeline:
            return ""
        
        workflow = {
            'name': f'{pipeline.name.title()} Pipeline',
            'on': {
                'schedule': [{'cron': pipeline.schedule}] if pipeline.trigger_type == 'schedule' else [],
                'workflow_dispatch': {} if pipeline.trigger_type == 'manual' else None,
                'push': {'branches': ['main']} if pipeline.trigger_type == 'git_push' else None
            },
            'jobs': {}
        }
        
        # Remover triggers vazios
        workflow['on'] = {k: v for k, v in workflow['on'].items() if v is not None}
        
        # Criar jobs para cada estágio
        for i, stage in enumerate(pipeline.stages):
            job_name = f'{pipeline.name}_{stage.name}'
            
            workflow['jobs'][job_name] = {
                'runs-on': 'ubuntu-latest',
                'needs': [f'{pipeline.name}_{pipeline.stages[j].name}' 
                         for j in range(i) if pipeline.stages[j].name in 
                         (stage.dependencies or [])],
                'steps': [
                    {
                        'name': 'Checkout code',
                        'uses': 'actions/checkout@v3'
                    },
                    {
                        'name': 'Set up Python',
                        'uses': 'actions/setup-python@v4',
                        'with': {'python-version': '3.9'}
                    },
                    {
                        'name': 'Install dependencies',
                        'run': 'pip install -r requirements_ml.txt'
                    }
                ]
            }
            
            # Adicionar comandos do estágio
            for command in stage.commands:
                workflow['jobs'][job_name]['steps'].append({
                    'name': f'Run: {command}',
                    'run': command,
                    'timeout-minutes': stage.timeout_minutes
                })
            
            # Adicionar upload de artifacts
            if pipeline.artifacts:
                workflow['jobs'][job_name]['steps'].append({
                    'name': 'Upload artifacts',
                    'uses': 'actions/upload-artifact@v3',
                    'with': {
                        'name': f'{pipeline.name}-{stage.name}-artifacts',
                        'path': 'ml_models/results/*'
                    }
                })
        
        # Salvar workflow
        workflow_file = self.config_dir / f"{pipeline_name}_workflow.yml"
        with open(workflow_file, 'w', encoding='utf-8') as f:
            yaml.dump(workflow, f, default_flow_style=False, indent=2)
        
        return str(workflow_file)
    
    def create_docker_compose(self, pipeline_name: str) -> str:
        """Cria docker-compose para um pipeline"""
        pipeline = self.get_pipeline_config(pipeline_name)
        if not pipeline:
            return ""
        
        compose = {
            'version': '3.8',
            'services': {
                f'{pipeline.name}_pipeline': {
                    'build': '.',
                    'image': f'apostapro/{pipeline.name}:{pipeline.version}',
                    'container_name': f'{pipeline.name}_pipeline',
                    'environment': self.get_environment_variables(pipeline.environment),
                    'volumes': [
                        './ml_models:/app/ml_models',
                        './data:/app/data',
                        './logs:/app/logs'
                    ],
                    'networks': ['apostapro_network'],
                    'restart': 'unless-stopped'
                }
            },
            'networks': {
                'apostapro_network': {
                    'driver': 'bridge'
                }
            }
        }
        
        # Salvar docker-compose
        compose_file = self.config_dir / f"{pipeline_name}_docker-compose.yml"
        with open(compose_file, 'w', encoding='utf-8') as f:
            yaml.dump(compose, f, default_flow_style=False, indent=2)
        
        return str(compose_file)
    
    def create_kubernetes_manifests(self, pipeline_name: str) -> List[str]:
        """Cria manifests do Kubernetes para um pipeline"""
        pipeline = self.get_pipeline_config(pipeline_name)
        if not pipeline:
            return []
        
        manifests = []
        
        # Deployment
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': f'{pipeline.name}-deployment',
                'namespace': 'apostapro-ml'
            },
            'spec': {
                'replicas': 1,
                'selector': {
                    'matchLabels': {'app': pipeline.name}
                },
                'template': {
                    'metadata': {'labels': {'app': pipeline.name}},
                    'spec': {
                        'containers': [{
                            'name': pipeline.name,
                            'image': f'apostapro/{pipeline.name}:{pipeline.version}',
                            'ports': [{'containerPort': 8080}],
                            'env': [
                                {'name': k, 'value': v} 
                                for k, v in self.get_environment_variables(pipeline.environment).items()
                            ],
                            'resources': {
                                'requests': {'memory': '512Mi', 'cpu': '250m'},
                                'limits': {'memory': '1Gi', 'cpu': '500m'}
                            }
                        }]
                    }
                }
            }
        }
        
        deployment_file = self.config_dir / f"{pipeline_name}_deployment.yml"
        with open(deployment_file, 'w', encoding='utf-8') as f:
            yaml.dump(deployment, f, default_flow_style=False, indent=2)
        manifests.append(str(deployment_file))
        
        # Service
        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f'{pipeline.name}-service',
                'namespace': 'apostapro-ml'
            },
            'spec': {
                'selector': {'app': pipeline.name},
                'ports': [{'port': 8080, 'targetPort': 8080}],
                'type': 'ClusterIP'
            }
        }
        
        service_file = self.config_dir / f"{pipeline.name}_service.yml"
        with open(service_file, 'w', encoding='utf-8') as f:
            yaml.dump(service, f, default_flow_style=False, indent=2)
        manifests.append(str(service_file))
        
        return manifests
    
    def save_config(self):
        """Salva configuração em arquivo JSON"""
        config_data = {
            'pipelines': {name: asdict(config) for name, config in self.pipelines.items()},
            'environments': self.environments,
            'notification_config': self.notification_config,
            'cache_config': self.cache_config
        }
        
        config_file = self.config_dir / "ci_cd_pipeline_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def load_config(self):
        """Carrega configuração de arquivo JSON"""
        config_file = self.config_dir / "ci_cd_pipeline_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Atualizar configurações
                if 'pipelines' in config_data:
                    for name, pipeline_data in config_data['pipelines'].items():
                        if name in self.pipelines:
                            # Atualizar configurações básicas
                            for key, value in pipeline_data.items():
                                if key != 'stages' and hasattr(self.pipelines[name], key):
                                    setattr(self.pipelines[name], key, value)
                
                logger.info("✅ Configuração de CI/CD carregada com sucesso")
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar configuração de CI/CD: {e}")

# Configuração global
ci_cd_config = CICDPipelineConfig()

if __name__ == "__main__":
    # Salvar configuração padrão
    ci_cd_config.save_config()
    print("✅ Configuração de CI/CD salva!")
    
    # Criar workflows para todos os pipelines
    for pipeline_name in ci_cd_config.pipelines.keys():
        workflow_file = ci_cd_config.create_github_actions_workflow(pipeline_name)
        print(f"✅ Workflow GitHub Actions criado: {workflow_file}")
        
        compose_file = ci_cd_config.create_docker_compose(pipeline_name)
        print(f"✅ Docker Compose criado: {compose_file}")
        
        k8s_manifests = ci_cd_config.create_kubernetes_manifests(pipeline_name)
        print(f"✅ Manifests Kubernetes criados: {len(k8s_manifests)} arquivos")
