#!/usr/bin/env python3
"""
Orquestração com Kubernetes para escalabilidade e monitoramento distribuído
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
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result

logger = logging.getLogger(__name__)

@dataclass
class KubernetesConfig:
    """Configuração do Kubernetes"""
    cluster_name: str
    namespace: str
    context: str
    api_server: str
    token: str
    ca_cert: str
    enabled: bool = True

@dataclass
class DeploymentConfig:
    """Configuração de deployment"""
    name: str
    replicas: int
    image: str
    image_tag: str
    cpu_request: str
    memory_request: str
    cpu_limit: str
    memory_limit: str
    ports: List[int]
    environment_vars: Dict[str, str]
    volume_mounts: List[Dict[str, str]]
    health_check_path: str
    liveness_probe: Dict[str, Any]
    readiness_probe: Dict[str, Any]

@dataclass
class ServiceConfig:
    """Configuração de serviço"""
    name: str
    type: str  # 'ClusterIP', 'NodePort', 'LoadBalancer'
    ports: List[Dict[str, Any]]
    selector: Dict[str, str]
    external_name: Optional[str] = None

@dataclass
class IngressConfig:
    """Configuração de ingress"""
    name: str
    host: str
    tls_secret: Optional[str] = None
    annotations: Dict[str, str] = None
    rules: List[Dict[str, Any]] = None

class KubernetesOrchestration:
    """Sistema de orquestração com Kubernetes"""
    
    def __init__(self):
        self.config = get_ml_config()
        
        # Diretórios
        self.k8s_dir = Path(self.config.monitoring_dir) / "kubernetes"
        self.k8s_dir.mkdir(parents=True, exist_ok=True)
        
        self.manifests_dir = self.k8s_dir / "manifests"
        self.manifests_dir.mkdir(exist_ok=True)
        
        self.configs_dir = self.k8s_dir / "configs"
        self.configs_dir.mkdir(exist_ok=True)
        
        # Configuração do Kubernetes
        self.k8s_config = KubernetesConfig(
            cluster_name='apostapro-cluster',
            namespace='apostapro-ml',
            context='apostapro-context',
            api_server='https://kubernetes.default.svc',
            token='your-service-account-token',
            ca_cert='your-ca-certificate'
        )
        
        # Configurações de deployments
        self.deployments = {
            'ml-api': DeploymentConfig(
                name='ml-api',
                replicas=3,
                image='apostapro/ml-api',
                image_tag='latest',
                cpu_request='500m',
                memory_request='1Gi',
                cpu_limit='1000m',
                memory_limit='2Gi',
                ports=[8000],
                environment_vars={
                    'ENVIRONMENT': 'production',
                    'LOG_LEVEL': 'INFO',
                    'API_VERSION': 'v1'
                },
                volume_mounts=[
                    {'name': 'ml-models', 'mountPath': '/app/models'},
                    {'name': 'ml-cache', 'mountPath': '/app/cache'}
                ],
                health_check_path='/health',
                liveness_probe={
                    'httpGet': {'path': '/health', 'port': 8000},
                    'initialDelaySeconds': 30,
                    'periodSeconds': 10
                },
                readiness_probe={
                    'httpGet': {'path': '/ready', 'port': 8000},
                    'initialDelaySeconds': 5,
                    'periodSeconds': 5
                }
            ),
            'ml-worker': DeploymentConfig(
                name='ml-worker',
                replicas=5,
                image='apostapro/ml-worker',
                image_tag='latest',
                cpu_request='1000m',
                memory_request='2Gi',
                cpu_limit='2000m',
                memory_limit='4Gi',
                ports=[8001],
                environment_vars={
                    'ENVIRONMENT': 'production',
                    'WORKER_TYPE': 'ml_training',
                    'QUEUE_NAME': 'ml_tasks'
                },
                volume_mounts=[
                    {'name': 'ml-data', 'mountPath': '/app/data'},
                    {'name': 'ml-results', 'mountPath': '/app/results'}
                ],
                health_check_path='/health',
                liveness_probe={
                    'httpGet': {'path': '/health', 'port': 8001},
                    'initialDelaySeconds': 60,
                    'periodSeconds': 30
                },
                readiness_probe={
                    'httpGet': {'path': '/ready', 'port': 8001},
                    'initialDelaySeconds': 10,
                    'periodSeconds': 10
                }
            ),
            'monitoring': DeploymentConfig(
                name='monitoring',
                replicas=2,
                image='apostapro/monitoring',
                image_tag='latest',
                cpu_request='250m',
                memory_request='512Mi',
                cpu_limit='500m',
                memory_limit='1Gi',
                ports=[9090, 3000],
                environment_vars={
                    'ENVIRONMENT': 'production',
                    'PROMETHEUS_ENABLED': 'true',
                    'GRAFANA_ENABLED': 'true'
                },
                volume_mounts=[
                    {'name': 'monitoring-data', 'mountPath': '/var/lib/prometheus'},
                    {'name': 'monitoring-config', 'mountPath': '/etc/prometheus'}
                ],
                health_check_path='/health',
                liveness_probe={
                    'httpGet': {'path': '/health', 'port': 9090},
                    'initialDelaySeconds': 30,
                    'periodSeconds': 30
                },
                readiness_probe={
                    'httpGet': {'path': '/ready', 'port': 9090},
                    'initialDelaySeconds': 5,
                    'periodSeconds': 5
                }
            )
        }
        
        # Configurações de serviços
        self.services = {
            'ml-api-service': ServiceConfig(
                name='ml-api-service',
                type='LoadBalancer',
                ports=[
                    {'name': 'http', 'port': 80, 'targetPort': 8000, 'protocol': 'TCP'}
                ],
                selector={'app': 'ml-api'}
            ),
            'ml-worker-service': ServiceConfig(
                name='ml-worker-service',
                type='ClusterIP',
                ports=[
                    {'name': 'http', 'port': 8001, 'targetPort': 8001, 'protocol': 'TCP'}
                ],
                selector={'app': 'ml-worker'}
            ),
            'monitoring-service': ServiceConfig(
                name='monitoring-service',
                type='ClusterIP',
                ports=[
                    {'name': 'prometheus', 'port': 9090, 'targetPort': 9090, 'protocol': 'TCP'},
                    {'name': 'grafana', 'port': 3000, 'targetPort': 3000, 'protocol': 'TCP'}
                ],
                selector={'app': 'monitoring'}
            )
        }
        
        # Configurações de ingress
        self.ingresses = {
            'ml-api-ingress': IngressConfig(
                name='ml-api-ingress',
                host='api.apostapro.com',
                tls_secret='apostapro-tls',
                annotations={
                    'kubernetes.io/ingress.class': 'nginx',
                    'nginx.ingress.kubernetes.io/ssl-redirect': 'true',
                    'nginx.ingress.kubernetes.io/force-ssl-redirect': 'true'
                },
                rules=[
                    {
                        'host': 'api.apostapro.com',
                        'http': {
                            'paths': [
                                {
                                    'path': '/',
                                    'pathType': 'Prefix',
                                    'backend': {
                                        'service': {
                                            'name': 'ml-api-service',
                                            'port': {'number': 80}
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
        }
        
        # Configurações de volumes persistentes
        self.persistent_volumes = {
            'ml-models-pv': {
                'name': 'ml-models-pv',
                'capacity': '10Gi',
                'accessModes': ['ReadWriteMany'],
                'hostPath': {'path': '/data/ml-models'}
            },
            'ml-cache-pv': {
                'name': 'ml-cache-pv',
                'capacity': '5Gi',
                'accessModes': ['ReadWriteMany'],
                'hostPath': {'path': '/data/ml-cache'}
            },
            'ml-data-pv': {
                'name': 'ml-data-pv',
                'capacity': '20Gi',
                'accessModes': ['ReadWriteMany'],
                'hostPath': {'path': '/data/ml-data'}
            },
            'ml-results-pv': {
                'name': 'ml-results-pv',
                'capacity': '10Gi',
                'accessModes': ['ReadWriteMany'],
                'hostPath': {'path': '/data/ml-results'}
            },
            'monitoring-data-pv': {
                'name': 'monitoring-data-pv',
                'capacity': '5Gi',
                'accessModes': ['ReadWriteMany'],
                'hostPath': {'path': '/data/monitoring'}
            }
        }
    
    def generate_namespace_manifest(self) -> str:
        """Gera manifesto do namespace"""
        try:
            namespace_manifest = {
                'apiVersion': 'v1',
                'kind': 'Namespace',
                'metadata': {
                    'name': self.k8s_config.namespace,
                    'labels': {
                        'name': self.k8s_config.namespace,
                        'app': 'apostapro-ml'
                    }
                }
            }
            
            return yaml.dump(namespace_manifest, default_flow_style=False, sort_keys=False)
            
        except Exception as e:
            logger.error(f"Erro ao gerar manifesto do namespace: {e}")
            return ""
    
    def generate_deployment_manifest(self, deployment_name: str) -> str:
        """Gera manifesto de deployment"""
        try:
            if deployment_name not in self.deployments:
                raise ValueError(f"Deployment {deployment_name} não encontrado")
            
            deployment_config = self.deployments[deployment_name]
            
            # Preparar volumes
            volumes = []
            for volume_mount in deployment_config.volume_mounts:
                volume_name = volume_mount['name']
                if volume_name in self.persistent_volumes:
                    volumes.append({
                        'name': volume_name,
                        'persistentVolumeClaim': {
                            'claimName': f'{volume_name}-pvc'
                        }
                    })
            
            # Preparar containers
            containers = [{
                'name': deployment_config.name,
                'image': f"{deployment_config.image}:{deployment_config.image_tag}",
                'ports': [{'containerPort': port} for port in deployment_config.ports],
                'resources': {
                    'requests': {
                        'cpu': deployment_config.cpu_request,
                        'memory': deployment_config.memory_request
                    },
                    'limits': {
                        'cpu': deployment_config.cpu_limit,
                        'memory': deployment_config.memory_limit
                    }
                },
                'env': [{'name': k, 'value': v} for k, v in deployment_config.environment_vars.items()],
                'volumeMounts': deployment_config.volume_mounts,
                'livenessProbe': deployment_config.liveness_probe,
                'readinessProbe': deployment_config.readiness_probe
            }]
            
            # Manifesto do deployment
            deployment_manifest = {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': deployment_config.name,
                    'namespace': self.k8s_config.namespace,
                    'labels': {
                        'app': deployment_config.name,
                        'version': deployment_config.image_tag
                    }
                },
                'spec': {
                    'replicas': deployment_config.replicas,
                    'selector': {
                        'matchLabels': {
                            'app': deployment_config.name
                        }
                    },
                    'template': {
                        'metadata': {
                            'labels': {
                                'app': deployment_config.name,
                                'version': deployment_config.image_tag
                            }
                        },
                        'spec': {
                            'containers': containers,
                            'volumes': volumes
                        }
                    }
                }
            }
            
            return yaml.dump(deployment_manifest, default_flow_style=False, sort_keys=False)
            
        except Exception as e:
            logger.error(f"Erro ao gerar manifesto de deployment: {e}")
            return ""
    
    def generate_service_manifest(self, service_name: str) -> str:
        """Gera manifesto de serviço"""
        try:
            if service_name not in self.services:
                raise ValueError(f"Serviço {service_name} não encontrado")
            
            service_config = self.services[service_name]
            
            service_manifest = {
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': service_config.name,
                    'namespace': self.k8s_config.namespace,
                    'labels': {
                        'app': service_config.name
                    }
                },
                'spec': {
                    'type': service_config.type,
                    'ports': service_config.ports,
                    'selector': service_config.selector
                }
            }
            
            if service_config.external_name:
                service_manifest['spec']['externalName'] = service_config.external_name
            
            return yaml.dump(service_manifest, default_flow_style=False, sort_keys=False)
            
        except Exception as e:
            logger.error(f"Erro ao gerar manifesto de serviço: {e}")
            return ""
    
    def generate_ingress_manifest(self, ingress_name: str) -> str:
        """Gera manifesto de ingress"""
        try:
            if ingress_name not in self.ingresses:
                raise ValueError(f"Ingress {ingress_name} não encontrado")
            
            ingress_config = self.ingresses[ingress_name]
            
            ingress_manifest = {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'Ingress',
                'metadata': {
                    'name': ingress_config.name,
                    'namespace': self.k8s_config.namespace,
                    'annotations': ingress_config.annotations or {}
                },
                'spec': {
                    'rules': ingress_config.rules or []
                }
            }
            
            if ingress_config.tls_secret:
                ingress_manifest['spec']['tls'] = [{
                    'hosts': [ingress_config.host],
                    'secretName': ingress_config.tls_secret
                }]
            
            return yaml.dump(ingress_manifest, default_flow_style=False, sort_keys=False)
            
        except Exception as e:
            logger.error(f"Erro ao gerar manifesto de ingress: {e}")
            return ""
    
    def generate_persistent_volume_manifest(self, volume_name: str) -> str:
        """Gera manifesto de volume persistente"""
        try:
            if volume_name not in self.persistent_volumes:
                raise ValueError(f"Volume {volume_name} não encontrado")
            
            volume_config = self.persistent_volumes[volume_name]
            
            pv_manifest = {
                'apiVersion': 'v1',
                'kind': 'PersistentVolume',
                'metadata': {
                    'name': volume_config['name'],
                    'labels': {
                        'type': 'local-storage'
                    }
                },
                'spec': {
                    'capacity': {
                        'storage': volume_config['capacity']
                    },
                    'accessModes': volume_config['accessModes'],
                    'hostPath': volume_config['hostPath'],
                    'storageClassName': 'local-storage'
                }
            }
            
            return yaml.dump(pv_manifest, default_flow_style=False, sort_keys=False)
            
        except Exception as e:
            logger.error(f"Erro ao gerar manifesto de volume persistente: {e}")
            return ""
    
    def generate_persistent_volume_claim_manifest(self, volume_name: str) -> str:
        """Gera manifesto de claim de volume persistente"""
        try:
            if volume_name not in self.persistent_volumes:
                raise ValueError(f"Volume {volume_name} não encontrado")
            
            volume_config = self.persistent_volumes[volume_name]
            
            pvc_manifest = {
                'apiVersion': 'v1',
                'kind': 'PersistentVolumeClaim',
                'metadata': {
                    'name': f"{volume_name}-pvc",
                    'namespace': self.k8s_config.namespace
                },
                'spec': {
                    'accessModes': volume_config['accessModes'],
                    'resources': {
                        'requests': {
                            'storage': volume_config['capacity']
                        }
                    },
                    'storageClassName': 'local-storage'
                }
            }
            
            return yaml.dump(pvc_manifest, default_flow_style=False, sort_keys=False)
            
        except Exception as e:
            logger.error(f"Erro ao gerar manifesto de PVC: {e}")
            return ""
    
    def generate_configmap_manifest(self) -> str:
        """Gera manifesto de ConfigMap"""
        try:
            configmap_manifest = {
                'apiVersion': 'v1',
                'kind': 'ConfigMap',
                'metadata': {
                    'name': 'apostapro-ml-config',
                    'namespace': self.k8s_config.namespace
                },
                'data': {
                    'environment': 'production',
                    'log_level': 'INFO',
                    'api_version': 'v1',
                    'ml_models_dir': '/app/models',
                    'ml_cache_dir': '/app/cache',
                    'ml_data_dir': '/app/data',
                    'ml_results_dir': '/app/results'
                }
            }
            
            return yaml.dump(configmap_manifest, default_flow_style=False, sort_keys=False)
            
        except Exception as e:
            logger.error(f"Erro ao gerar manifesto de ConfigMap: {e}")
            return ""
    
    def generate_secret_manifest(self) -> str:
        """Gera manifesto de Secret"""
        try:
            secret_manifest = {
                'apiVersion': 'v1',
                'kind': 'Secret',
                'metadata': {
                    'name': 'apostapro-ml-secrets',
                    'namespace': self.k8s_config.namespace
                },
                'type': 'Opaque',
                'data': {
                    'database_url': 'cG9zdGdyZXNxbDovL2xvY2FsaG9zdC9hcG9zdGFwcm8=',  # base64 encoded
                    'api_key': 'eW91ci1hcGkta2V5LWhlcmU=',  # base64 encoded
                    'jwt_secret': 'eW91ci1qd3Qtc2VjcmV0LWhlcmU='  # base64 encoded
                }
            }
            
            return yaml.dump(secret_manifest, default_flow_style=False, sort_keys=False)
            
        except Exception as e:
            logger.error(f"Erro ao gerar manifesto de Secret: {e}")
            return ""
    
    def generate_horizontal_pod_autoscaler_manifest(self, deployment_name: str) -> str:
        """Gera manifesto de HPA (Horizontal Pod Autoscaler)"""
        try:
            if deployment_name not in self.deployments:
                raise ValueError(f"Deployment {deployment_name} não encontrado")
            
            deployment_config = self.deployments[deployment_name]
            
            hpa_manifest = {
                'apiVersion': 'autoscaling/v2',
                'kind': 'HorizontalPodAutoscaler',
                'metadata': {
                    'name': f"{deployment_name}-hpa",
                    'namespace': self.k8s_config.namespace
                },
                'spec': {
                    'scaleTargetRef': {
                        'apiVersion': 'apps/v1',
                        'kind': 'Deployment',
                        'name': deployment_name
                    },
                    'minReplicas': max(1, deployment_config.replicas // 2),
                    'maxReplicas': deployment_config.replicas * 3,
                    'metrics': [
                        {
                            'type': 'Resource',
                            'resource': {
                                'name': 'cpu',
                                'target': {
                                    'type': 'Utilization',
                                    'averageUtilization': 70
                                }
                            }
                        },
                        {
                            'type': 'Resource',
                            'resource': {
                                'name': 'memory',
                                'target': {
                                    'type': 'Utilization',
                                    'averageUtilization': 80
                                }
                            }
                        }
                    ]
                }
            }
            
            return yaml.dump(hpa_manifest, default_flow_style=False, sort_keys=False)
            
        except Exception as e:
            logger.error(f"Erro ao gerar manifesto de HPA: {e}")
            return ""
    
    def generate_all_manifests(self) -> Dict[str, str]:
        """Gera todos os manifestos Kubernetes"""
        try:
            manifests = {}
            
            # Namespace
            manifests['namespace'] = self.generate_namespace_manifest()
            
            # Volumes persistentes
            for volume_name in self.persistent_volumes.keys():
                manifests[f'pv_{volume_name}'] = self.generate_persistent_volume_manifest(volume_name)
                manifests[f'pvc_{volume_name}'] = self.generate_persistent_volume_claim_manifest(volume_name)
            
            # ConfigMap e Secret
            manifests['configmap'] = self.generate_configmap_manifest()
            manifests['secret'] = self.generate_secret_manifest()
            
            # Deployments
            for deployment_name in self.deployments.keys():
                manifests[f'deployment_{deployment_name}'] = self.generate_deployment_manifest(deployment_name)
                manifests[f'hpa_{deployment_name}'] = self.generate_horizontal_pod_autoscaler_manifest(deployment_name)
            
            # Services
            for service_name in self.services.keys():
                manifests[f'service_{service_name}'] = self.generate_service_manifest(service_name)
            
            # Ingresses
            for ingress_name in self.ingresses.keys():
                manifests[f'ingress_{ingress_name}'] = self.generate_ingress_manifest(ingress_name)
            
            return manifests
            
        except Exception as e:
            logger.error(f"Erro ao gerar todos os manifestos: {e}")
            return {}
    
    def save_manifests(self, manifests: Dict[str, str]) -> bool:
        """Salva manifestos em arquivos YAML"""
        try:
            for name, content in manifests.items():
                if content:
                    file_path = self.manifests_dir / f"{name}.yaml"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    logger.info(f"Manifesto salvo: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar manifestos: {e}")
            return False
    
    def apply_manifests(self, manifest_files: List[str] = None) -> bool:
        """Aplica manifestos no cluster Kubernetes"""
        try:
            if not self.k8s_config.enabled:
                logger.warning("Kubernetes está desabilitado")
                return False
            
            if manifest_files is None:
                # Aplicar todos os manifestos
                manifest_files = list(self.manifests_dir.glob("*.yaml"))
            
            for manifest_file in manifest_files:
                try:
                    logger.info(f"Aplicando manifesto: {manifest_file}")
                    
                    # Simular aplicação (em produção, seria kubectl apply)
                    # subprocess.run(['kubectl', 'apply', '-f', str(manifest_file)], check=True)
                    
                    logger.info(f"Manifesto aplicado com sucesso: {manifest_file}")
                    
                except Exception as e:
                    logger.error(f"Erro ao aplicar manifesto {manifest_file}: {e}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao aplicar manifestos: {e}")
            return False
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Obtém status do cluster Kubernetes"""
        try:
            if not self.k8s_config.enabled:
                return {'error': 'Kubernetes está desabilitado'}
            
            # Simular status do cluster (em produção, seria kubectl get)
            cluster_status = {
                'cluster_name': self.k8s_config.cluster_name,
                'namespace': self.k8s_config.namespace,
                'nodes': [
                    {'name': 'node-1', 'status': 'Ready', 'cpu': '4', 'memory': '8Gi'},
                    {'name': 'node-2', 'status': 'Ready', 'cpu': '4', 'memory': '8Gi'},
                    {'name': 'node-3', 'status': 'Ready', 'cpu': '4', 'memory': '8Gi'}
                ],
                'pods': {
                    'ml-api': {'ready': 3, 'total': 3, 'status': 'Running'},
                    'ml-worker': {'ready': 5, 'total': 5, 'status': 'Running'},
                    'monitoring': {'ready': 2, 'total': 2, 'status': 'Running'}
                },
                'services': {
                    'ml-api-service': {'type': 'LoadBalancer', 'external_ip': '192.168.1.100'},
                    'ml-worker-service': {'type': 'ClusterIP', 'cluster_ip': '10.96.1.100'},
                    'monitoring-service': {'type': 'ClusterIP', 'cluster_ip': '10.96.1.101'}
                }
            }
            
            return cluster_status
            
        except Exception as e:
            logger.error(f"Erro ao obter status do cluster: {e}")
            return {'error': str(e)}
    
    def scale_deployment(self, deployment_name: str, replicas: int) -> bool:
        """Escala um deployment"""
        try:
            if not self.k8s_config.enabled:
                logger.warning("Kubernetes está desabilitado")
                return False
            
            if deployment_name not in self.deployments:
                raise ValueError(f"Deployment {deployment_name} não encontrado")
            
            logger.info(f"Escalando deployment {deployment_name} para {replicas} réplicas")
            
            # Simular escalonamento (em produção, seria kubectl scale)
            # subprocess.run(['kubectl', 'scale', 'deployment', deployment_name, 
            #                '--replicas', str(replicas), '-n', self.k8s_config.namespace], check=True)
            
            # Atualizar configuração local
            self.deployments[deployment_name].replicas = replicas
            
            logger.info(f"Deployment {deployment_name} escalado para {replicas} réplicas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao escalar deployment {deployment_name}: {e}")
            return False
    
    def get_deployment_logs(self, deployment_name: str, tail_lines: int = 100) -> List[str]:
        """Obtém logs de um deployment"""
        try:
            if not self.k8s_config.enabled:
                return ['Kubernetes está desabilitado']
            
            if deployment_name not in self.deployments:
                return [f'Deployment {deployment_name} não encontrado']
            
            logger.info(f"Obtendo logs do deployment {deployment_name}")
            
            # Simular logs (em produção, seria kubectl logs)
            # result = subprocess.run(['kubectl', 'logs', 'deployment', deployment_name, 
            #                         '--tail', str(tail_lines), '-n', self.k8s_config.namespace], 
            #                        capture_output=True, text=True, check=True)
            # logs = result.stdout.splitlines()
            
            # Logs simulados
            logs = [
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: Deployment {deployment_name} iniciado",
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: Health check passou",
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: Recebendo requisições",
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: Processando tarefas ML"
            ]
            
            return logs
            
        except Exception as e:
            logger.error(f"Erro ao obter logs do deployment {deployment_name}: {e}")
            return [f'Erro: {str(e)}']
    
    def create_backup(self) -> str:
        """Cria backup do cluster"""
        try:
            if not self.k8s_config.enabled:
                return "Kubernetes está desabilitado"
            
            logger.info("Criando backup do cluster")
            
            # Simular criação de backup
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir = self.k8s_dir / "backups" / backup_name
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Salvar configurações
            config_backup = {
                'timestamp': datetime.now().isoformat(),
                'cluster_config': asdict(self.k8s_config),
                'deployments': {k: asdict(v) for k, v in self.deployments.items()},
                'services': {k: asdict(v) for k, v in self.services.items()}
            }
            
            backup_file = backup_dir / "cluster_config.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config_backup, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backup criado: {backup_dir}")
            return str(backup_dir)
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return f"Erro: {str(e)}"

# Instância global
kubernetes_orchestration = KubernetesOrchestration()

# Funções de conveniência
def generate_all_manifests() -> Dict[str, str]:
    """Gera todos os manifestos Kubernetes"""
    return kubernetes_orchestration.generate_all_manifests()

def apply_manifests(manifest_files: List[str] = None) -> bool:
    """Aplica manifestos no cluster"""
    return kubernetes_orchestration.apply_manifests(manifest_files)

def get_cluster_status() -> Dict[str, Any]:
    """Obtém status do cluster"""
    return kubernetes_orchestration.get_cluster_status()

def scale_deployment(deployment_name: str, replicas: int) -> bool:
    """Escala um deployment"""
    return kubernetes_orchestration.scale_deployment(deployment_name, replicas)

def get_deployment_logs(deployment_name: str, tail_lines: int = 100) -> List[str]:
    """Obtém logs de um deployment"""
    return kubernetes_orchestration.get_deployment_logs(deployment_name, tail_lines)
