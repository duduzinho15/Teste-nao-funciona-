#!/usr/bin/env python3
"""
Configuração de Kubernetes com monitoramento distribuído e auto-scaling
"""
import os
import yaml
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta

@dataclass
class KubernetesNamespace:
    """Configuração de namespace Kubernetes"""
    name: str
    description: str
    labels: Dict[str, str] = None
    resource_quota: Dict[str, str] = None

@dataclass
class KubernetesDeployment:
    """Configuração de deployment Kubernetes"""
    name: str
    image: str
    image_tag: str
    replicas: int
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
    auto_scaling: bool = True
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80

@dataclass
class KubernetesService:
    """Configuração de serviço Kubernetes"""
    name: str
    type: str  # 'ClusterIP', 'NodePort', 'LoadBalancer'
    ports: List[Dict[str, Any]]
    selector: Dict[str, str]
    external_name: Optional[str] = None
    annotations: Dict[str, str] = None

@dataclass
class KubernetesIngress:
    """Configuração de ingress Kubernetes"""
    name: str
    host: str
    tls_secret: Optional[str] = None
    annotations: Dict[str, str] = None
    rules: List[Dict[str, Any]] = None

@dataclass
class MonitoringConfig:
    """Configuração de monitoramento"""
    prometheus_enabled: bool = True
    grafana_enabled: bool = True
    alertmanager_enabled: bool = True
    node_exporter_enabled: bool = True
    cadvisor_enabled: bool = True
    custom_metrics_enabled: bool = True

class KubernetesMonitoringConfig:
    """Configuração centralizada para Kubernetes com monitoramento"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "configs"
        self.config_dir.mkdir(exist_ok=True)
        
        # Namespaces
        self.namespaces = {
            'apostapro-ml': KubernetesNamespace(
                name='apostapro-ml',
                description='Namespace para aplicações de Machine Learning',
                labels={'app': 'apostapro', 'component': 'ml'},
                resource_quota={
                    'requests.cpu': '4',
                    'requests.memory': '8Gi',
                    'limits.cpu': '8',
                    'limits.memory': '16Gi'
                }
            ),
            'monitoring': KubernetesNamespace(
                name='monitoring',
                description='Namespace para ferramentas de monitoramento',
                labels={'app': 'apostapro', 'component': 'monitoring'}
            ),
            'logging': KubernetesNamespace(
                name='logging',
                description='Namespace para sistema de logging',
                labels={'app': 'apostapro', 'component': 'logging'}
            )
        }
        
        # Deployments principais
        self.deployments = {
            'ml-api': KubernetesDeployment(
                name='ml-api',
                image='apostapro/ml-api',
                image_tag='latest',
                replicas=3,
                cpu_request='500m',
                memory_request='1Gi',
                cpu_limit='1000m',
                memory_limit='2Gi',
                ports=[8080, 9090],
                environment_vars={
                    'ML_ENV': 'production',
                    'LOG_LEVEL': 'INFO',
                    'API_VERSION': 'v1'
                },
                volume_mounts=[
                    {'name': 'ml-models', 'mountPath': '/app/models'},
                    {'name': 'ml-data', 'mountPath': '/app/data'}
                ],
                health_check_path='/health',
                liveness_probe={
                    'httpGet': {'path': '/health', 'port': 8080},
                    'initialDelaySeconds': 30,
                    'periodSeconds': 10
                },
                readiness_probe={
                    'httpGet': {'path': '/ready', 'port': 8080},
                    'initialDelaySeconds': 5,
                    'periodSeconds': 5
                },
                auto_scaling=True,
                min_replicas=2,
                max_replicas=10,
                target_cpu_utilization=70
            ),
            
            'ml-training': KubernetesDeployment(
                name='ml-training',
                image='apostapro/ml-training',
                image_tag='latest',
                replicas=2,
                cpu_request='1000m',
                memory_request='2Gi',
                cpu_limit='2000m',
                memory_limit='4Gi',
                ports=[8080],
                environment_vars={
                    'ML_ENV': 'production',
                    'LOG_LEVEL': 'INFO',
                    'TRAINING_MODE': 'distributed'
                },
                volume_mounts=[
                    {'name': 'ml-models', 'mountPath': '/app/models'},
                    {'name': 'ml-data', 'mountPath': '/app/data'},
                    {'name': 'ml-cache', 'mountPath': '/app/cache'}
                ],
                health_check_path='/health',
                liveness_probe={
                    'httpGet': {'path': '/health', 'port': 8080},
                    'initialDelaySeconds': 60,
                    'periodSeconds': 30
                },
                readiness_probe={
                    'httpGet': {'path': '/ready', 'port': 8080},
                    'initialDelaySeconds': 30,
                    'periodSeconds': 10
                },
                auto_scaling=True,
                min_replicas=1,
                max_replicas=5,
                target_cpu_utilization=80
            ),
            
            'ml-inference': KubernetesDeployment(
                name='ml-inference',
                image='apostapro/ml-inference',
                image_tag='latest',
                replicas=5,
                cpu_request='250m',
                memory_request='512Mi',
                cpu_limit='500m',
                memory_limit='1Gi',
                ports=[8080],
                environment_vars={
                    'ML_ENV': 'production',
                    'LOG_LEVEL': 'INFO',
                    'INFERENCE_MODE': 'real-time'
                },
                volume_mounts=[
                    {'name': 'ml-models', 'mountPath': '/app/models'},
                    {'name': 'ml-cache', 'mountPath': '/app/cache'}
                ],
                health_check_path='/health',
                liveness_probe={
                    'httpGet': {'path': '/health', 'port': 8080},
                    'initialDelaySeconds': 15,
                    'periodSeconds': 10
                },
                readiness_probe={
                    'httpGet': {'path': '/ready', 'port': 8080},
                    'initialDelaySeconds': 5,
                    'periodSeconds': 5
                },
                auto_scaling=True,
                min_replicas=3,
                max_replicas=15,
                target_cpu_utilization=75
            )
        }
        
        # Serviços
        self.services = {
            'ml-api-service': KubernetesService(
                name='ml-api-service',
                type='LoadBalancer',
                ports=[
                    {'name': 'http', 'port': 80, 'targetPort': 8080},
                    {'name': 'metrics', 'port': 9090, 'targetPort': 9090}
                ],
                selector={'app': 'ml-api'},
                annotations={
                    'service.beta.kubernetes.io/aws-load-balancer-type': 'nlb',
                    'service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled': 'true'
                }
            ),
            
            'ml-training-service': KubernetesService(
                name='ml-training-service',
                type='ClusterIP',
                ports=[{'name': 'http', 'port': 8080, 'targetPort': 8080}],
                selector={'app': 'ml-training'}
            ),
            
            'ml-inference-service': KubernetesService(
                name='ml-inference-service',
                type='ClusterIP',
                ports=[{'name': 'http', 'port': 8080, 'targetPort': 8080}],
                selector={'app': 'ml-inference'}
            )
        }
        
        # Ingress
        self.ingresses = {
            'ml-api-ingress': KubernetesIngress(
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
        
        # Configuração de monitoramento
        self.monitoring = MonitoringConfig(
            prometheus_enabled=True,
            grafana_enabled=True,
            alertmanager_enabled=True,
            node_exporter_enabled=True,
            cadvisor_enabled=True,
            custom_metrics_enabled=True
        )
        
        # Configurações de recursos
        self.resource_config = {
            'storage_class': 'gp2',  # AWS EBS
            'persistent_volumes': {
                'ml-models': {
                    'size': '10Gi',
                    'access_mode': 'ReadWriteMany',
                    'storage_class': 'gp2'
                },
                'ml-data': {
                    'size': '100Gi',
                    'access_mode': 'ReadWriteMany',
                    'storage_class': 'gp2'
                },
                'ml-cache': {
                    'size': '50Gi',
                    'access_mode': 'ReadWriteMany',
                    'storage_class': 'gp2'
                }
            },
            'config_maps': {
                'ml-config': {
                    'ML_ENV': 'production',
                    'LOG_LEVEL': 'INFO',
                    'API_VERSION': 'v1'
                }
            },
            'secrets': {
                'ml-secrets': {
                    'API_KEYS': 'base64_encoded_api_keys',
                    'DATABASE_URL': 'base64_encoded_db_url'
                }
            }
        }
    
    def create_namespace_manifests(self) -> List[str]:
        """Cria manifests para namespaces"""
        manifests = []
        
        for namespace in self.namespaces.values():
            manifest = {
                'apiVersion': 'v1',
                'kind': 'Namespace',
                'metadata': {
                    'name': namespace.name,
                    'description': namespace.description,
                    'labels': namespace.labels or {}
                }
            }
            
            # Adicionar ResourceQuota se especificado
            if namespace.resource_quota:
                quota_manifest = {
                    'apiVersion': 'v1',
                    'kind': 'ResourceQuota',
                    'metadata': {
                        'name': f'{namespace.name}-quota',
                        'namespace': namespace.name
                    },
                    'spec': {
                        'hard': namespace.resource_quota
                    }
                }
                
                quota_file = self.config_dir / f"{namespace.name}_quota.yml"
                with open(quota_file, 'w', encoding='utf-8') as f:
                    yaml.dump(quota_manifest, f, default_flow_style=False, indent=2)
                manifests.append(str(quota_file))
            
            # Salvar namespace
            namespace_file = self.config_dir / f"{namespace.name}_namespace.yml"
            with open(namespace_file, 'w', encoding='utf-8') as f:
                yaml.dump(manifest, f, default_flow_style=False, indent=2)
            manifests.append(str(namespace_file))
        
        return manifests
    
    def create_deployment_manifests(self) -> List[str]:
        """Cria manifests para deployments"""
        manifests = []
        
        for deployment in self.deployments.values():
            # Deployment
            deployment_manifest = {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': deployment.name,
                    'namespace': 'apostapro-ml',
                    'labels': {'app': deployment.name}
                },
                'spec': {
                    'replicas': deployment.replicas,
                    'selector': {
                        'matchLabels': {'app': deployment.name}
                    },
                    'template': {
                        'metadata': {
                            'labels': {'app': deployment.name}
                        },
                        'spec': {
                            'containers': [{
                                'name': deployment.name,
                                'image': f'{deployment.image}:{deployment.image_tag}',
                                'ports': [{'containerPort': port} for port in deployment.ports],
                                'env': [
                                    {'name': k, 'value': v} 
                                    for k, v in deployment.environment_vars.items()
                                ],
                                'volumeMounts': deployment.volume_mounts,
                                'livenessProbe': deployment.liveness_probe,
                                'readinessProbe': deployment.readiness_probe,
                                'resources': {
                                    'requests': {
                                        'cpu': deployment.cpu_request,
                                        'memory': deployment.memory_request
                                    },
                                    'limits': {
                                        'cpu': deployment.cpu_limit,
                                        'memory': deployment.memory_limit
                                    }
                                }
                            }],
                            'volumes': [
                                {
                                    'name': mount['name'],
                                    'persistentVolumeClaim': {
                                        'claimName': f'{mount["name"]}-pvc'
                                    }
                                }
                                for mount in deployment.volume_mounts
                            ]
                        }
                    }
                }
            }
            
            deployment_file = self.config_dir / f"{deployment.name}_deployment.yml"
            with open(deployment_file, 'w', encoding='utf-8') as f:
                yaml.dump(deployment_manifest, f, default_flow_style=False, indent=2)
            manifests.append(str(deployment_file))
            
            # HorizontalPodAutoscaler se habilitado
            if deployment.auto_scaling:
                hpa_manifest = {
                    'apiVersion': 'autoscaling/v2',
                    'kind': 'HorizontalPodAutoscaler',
                    'metadata': {
                        'name': f'{deployment.name}-hpa',
                        'namespace': 'apostapro-ml'
                    },
                    'spec': {
                        'scaleTargetRef': {
                            'apiVersion': 'apps/v1',
                            'kind': 'Deployment',
                            'name': deployment.name
                        },
                        'minReplicas': deployment.min_replicas,
                        'maxReplicas': deployment.max_replicas,
                        'metrics': [
                            {
                                'type': 'Resource',
                                'resource': {
                                    'name': 'cpu',
                                    'target': {
                                        'type': 'Utilization',
                                        'averageUtilization': deployment.target_cpu_utilization
                                    }
                                }
                            },
                            {
                                'type': 'Resource',
                                'resource': {
                                    'name': 'memory',
                                    'target': {
                                        'type': 'Utilization',
                                        'averageUtilization': deployment.target_memory_utilization
                                    }
                                }
                            }
                        ]
                    }
                }
                
                hpa_file = self.config_dir / f"{deployment.name}_hpa.yml"
                with open(hpa_file, 'w', encoding='utf-8') as f:
                    yaml.dump(hpa_manifest, f, default_flow_style=False, indent=2)
                manifests.append(str(hpa_file))
        
        return manifests
    
    def create_service_manifests(self) -> List[str]:
        """Cria manifests para serviços"""
        manifests = []
        
        for service in self.services.values():
            service_manifest = {
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': service.name,
                    'namespace': 'apostapro-ml',
                    'annotations': service.annotations or {}
                },
                'spec': {
                    'type': service.type,
                    'selector': service.selector,
                    'ports': service.ports
                }
            }
            
            if service.external_name:
                service_manifest['spec']['externalName'] = service.external_name
            
            service_file = self.config_dir / f"{service.name}_service.yml"
            with open(service_file, 'w', encoding='utf-8') as f:
                yaml.dump(service_manifest, f, default_flow_style=False, indent=2)
            manifests.append(str(service_file))
        
        return manifests
    
    def create_ingress_manifests(self) -> List[str]:
        """Cria manifests para ingress"""
        manifests = []
        
        for ingress in self.ingresses.values():
            ingress_manifest = {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'Ingress',
                'metadata': {
                    'name': ingress.name,
                    'namespace': 'apostapro-ml',
                    'annotations': ingress.annotations or {}
                },
                'spec': {
                    'rules': ingress.rules or []
                }
            }
            
            if ingress.tls_secret:
                ingress_manifest['spec']['tls'] = [{
                    'hosts': [ingress.host],
                    'secretName': ingress.tls_secret
                }]
            
            ingress_file = self.config_dir / f"{ingress.name}_ingress.yml"
            with open(ingress_file, 'w', encoding='utf-8') as f:
                yaml.dump(ingress_manifest, f, default_flow_style=False, indent=2)
            manifests.append(str(ingress_file))
        
        return manifests
    
    def create_monitoring_manifests(self) -> List[str]:
        """Cria manifests para monitoramento"""
        manifests = []
        
        if self.monitoring.prometheus_enabled:
            # Prometheus
            prometheus_manifest = {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': 'prometheus',
                    'namespace': 'monitoring'
                },
                'spec': {
                    'replicas': 1,
                    'selector': {'matchLabels': {'app': 'prometheus'}},
                    'template': {
                        'metadata': {'labels': {'app': 'prometheus'}},
                        'spec': {
                            'containers': [{
                                'name': 'prometheus',
                                'image': 'prom/prometheus:latest',
                                'ports': [{'containerPort': 9090}],
                                'volumeMounts': [
                                    {'name': 'prometheus-config', 'mountPath': '/etc/prometheus'},
                                    {'name': 'prometheus-data', 'mountPath': '/prometheus'}
                                ]
                            }],
                            'volumes': [
                                {'name': 'prometheus-config', 'configMap': {'name': 'prometheus-config'}},
                                {'name': 'prometheus-data', 'emptyDir': {}}
                            ]
                        }
                    }
                }
            }
            
            prometheus_file = self.config_dir / "prometheus_deployment.yml"
            with open(prometheus_file, 'w', encoding='utf-8') as f:
                yaml.dump(prometheus_manifest, f, default_flow_style=False, indent=2)
            manifests.append(str(prometheus_file))
        
        if self.monitoring.grafana_enabled:
            # Grafana
            grafana_manifest = {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': 'grafana',
                    'namespace': 'monitoring'
                },
                'spec': {
                    'replicas': 1,
                    'selector': {'matchLabels': {'app': 'grafana'}},
                    'template': {
                        'metadata': {'labels': {'app': 'grafana'}},
                        'spec': {
                            'containers': [{
                                'name': 'grafana',
                                'image': 'grafana/grafana:latest',
                                'ports': [{'containerPort': 3000}],
                                'env': [
                                    {'name': 'GF_SECURITY_ADMIN_PASSWORD', 'value': 'admin'},
                                    {'name': 'GF_USERS_ALLOW_SIGN_UP', 'value': 'false'}
                                ]
                            }]
                        }
                    }
                }
            }
            
            grafana_file = self.config_dir / "grafana_deployment.yml"
            with open(grafana_file, 'w', encoding='utf-8') as f:
                yaml.dump(grafana_manifest, f, default_flow_style=False, indent=2)
            manifests.append(str(grafana_file))
        
        return manifests
    
    def create_persistent_volume_claims(self) -> List[str]:
        """Cria PersistentVolumeClaims"""
        manifests = []
        
        for name, config in self.resource_config['persistent_volumes'].items():
            pvc_manifest = {
                'apiVersion': 'v1',
                'kind': 'PersistentVolumeClaim',
                'metadata': {
                    'name': f'{name}-pvc',
                    'namespace': 'apostapro-ml'
                },
                'spec': {
                    'accessModes': [config['access_mode']],
                    'resources': {
                        'requests': {
                            'storage': config['size']
                        }
                    },
                    'storageClassName': config['storage_class']
                }
            }
            
            pvc_file = self.config_dir / f"{name}_pvc.yml"
            with open(pvc_file, 'w', encoding='utf-8') as f:
                yaml.dump(pvc_manifest, f, default_flow_style=False, indent=2)
            manifests.append(str(pvc_file))
        
        return manifests
    
    def create_all_manifests(self) -> Dict[str, List[str]]:
        """Cria todos os manifests Kubernetes"""
        manifests = {
            'namespaces': self.create_namespace_manifests(),
            'deployments': self.create_deployment_manifests(),
            'services': self.create_service_manifests(),
            'ingresses': self.create_ingress_manifests(),
            'monitoring': self.create_monitoring_manifests(),
            'persistent_volumes': self.create_persistent_volume_claims()
        }
        
        return manifests
    
    def save_config(self):
        """Salva configuração em arquivo JSON"""
        config_data = {
            'namespaces': {name: asdict(ns) for name, ns in self.namespaces.items()},
            'deployments': {name: asdict(dep) for name, dep in self.deployments.items()},
            'services': {name: asdict(svc) for name, svc in self.services.items()},
            'ingresses': {name: asdict(ing) for name, ing in self.ingresses.items()},
            'monitoring': asdict(self.monitoring),
            'resource_config': self.resource_config
        }
        
        config_file = self.config_dir / "kubernetes_monitoring_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

# Configuração global
k8s_monitoring_config = KubernetesMonitoringConfig()

if __name__ == "__main__":
    # Salvar configuração padrão
    k8s_monitoring_config.save_config()
    print("✅ Configuração de Kubernetes com monitoramento salva!")
    
    # Criar todos os manifests
    all_manifests = k8s_monitoring_config.create_all_manifests()
    
    total_manifests = sum(len(manifests) for manifests in all_manifests.values())
    print(f"✅ Total de {total_manifests} manifests Kubernetes criados:")
    
    for category, manifests in all_manifests.items():
        print(f"  - {category}: {len(manifests)} arquivos")
        for manifest in manifests:
            print(f"    * {manifest}")
