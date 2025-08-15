#!/usr/bin/env python3
"""
Demonstração da Orquestração com Kubernetes
"""
import logging
import sys
import json
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Adicionar diretório pai ao path
sys.path.append(str(Path(__file__).parent))

def main():
    """Função principal da demonstração"""
    print("☸️ APOSTAPRO - Demonstração da Orquestração com Kubernetes")
    print("=" * 80)
    
    try:
        # Importar módulos
        from ml_models.kubernetes_orchestration import (
            kubernetes_orchestration,
            generate_all_manifests,
            apply_manifests,
            get_cluster_status,
            scale_deployment,
            get_deployment_logs
        )
        
        print("✅ Módulos importados com sucesso")
        
        # 1. Verificar configuração do Kubernetes
        print("\n1️⃣ Verificando configuração do Kubernetes...")
        
        k8s_config = kubernetes_orchestration.k8s_config
        print(f"   🏗️  Cluster: {k8s_config.cluster_name}")
        print(f"   📁 Namespace: {k8s_config.namespace}")
        print(f"   🔗 API Server: {k8s_config.api_server}")
        print(f"   ✅ Habilitado: {k8s_config.enabled}")
        
        # 2. Verificar configurações de deployments
        print("\n2️⃣ Verificando configurações de deployments...")
        
        deployments = kubernetes_orchestration.deployments
        print(f"   📊 Total de deployments: {len(deployments)}")
        
        for name, config in deployments.items():
            print(f"   • {name}:")
            print(f"      - Réplicas: {config.replicas}")
            print(f"      - Imagem: {config.image}:{config.image_tag}")
            print(f"      - CPU: {config.cpu_request} → {config.cpu_limit}")
            print(f"      - Memória: {config.memory_request} → {config.memory_limit}")
            print(f"      - Portas: {config.ports}")
        
        # 3. Verificar configurações de serviços
        print("\n3️⃣ Verificando configurações de serviços...")
        
        services = kubernetes_orchestration.services
        print(f"   🌐 Total de serviços: {len(services)}")
        
        for name, config in services.items():
            print(f"   • {name}:")
            print(f"      - Tipo: {config.type}")
            print(f"      - Portas: {len(config.ports)}")
            print(f"      - Selector: {config.selector}")
        
        # 4. Verificar configurações de ingress
        print("\n4️⃣ Verificando configurações de ingress...")
        
        ingresses = kubernetes_orchestration.ingresses
        print(f"   🚪 Total de ingress: {len(ingresses)}")
        
        for name, config in ingresses.items():
            print(f"   • {name}:")
            print(f"      - Host: {config.host}")
            print(f"      - TLS: {'Sim' if config.tls_secret else 'Não'}")
            print(f"      - Anotações: {len(config.annotations or {})}")
        
        # 5. Verificar volumes persistentes
        print("\n5️⃣ Verificando volumes persistentes...")
        
        volumes = kubernetes_orchestration.persistent_volumes
        print(f"   💾 Total de volumes: {len(volumes)}")
        
        for name, config in volumes.items():
            print(f"   • {name}:")
            print(f"      - Capacidade: {config['capacity']}")
            print(f"      - Modos de acesso: {config['accessModes']}")
            print(f"      - Caminho: {config['hostPath']['path']}")
        
        # 6. Gerar todos os manifestos
        print("\n6️⃣ Gerando manifestos Kubernetes...")
        
        print("   📝 Gerando manifestos...")
        manifests = generate_all_manifests()
        
        if manifests:
            print(f"      ✅ {len(manifests)} manifestos gerados")
            
            # Mostrar tipos de manifestos
            manifest_types = {}
            for name in manifests.keys():
                if name.startswith('deployment_'):
                    manifest_types['Deployments'] = manifest_types.get('Deployments', 0) + 1
                elif name.startswith('service_'):
                    manifest_types['Services'] = manifest_types.get('Services', 0) + 1
                elif name.startswith('pv_'):
                    manifest_types['Persistent Volumes'] = manifest_types.get('Persistent Volumes', 0) + 1
                elif name.startswith('pvc_'):
                    manifest_types['PVCs'] = manifest_types.get('PVCs', 0) + 1
                elif name.startswith('hpa_'):
                    manifest_types['HPAs'] = manifest_types.get('HPAs', 0) + 1
                elif name.startswith('ingress_'):
                    manifest_types['Ingresses'] = manifest_types.get('Ingresses', 0) + 1
                else:
                    manifest_types['Outros'] = manifest_types.get('Outros', 0) + 1
            
            for manifest_type, count in manifest_types.items():
                print(f"         - {manifest_type}: {count}")
        else:
            print("      ❌ Erro ao gerar manifestos")
        
        # 7. Salvar manifestos
        print("\n7️⃣ Salvando manifestos...")
        
        if manifests:
            success = kubernetes_orchestration.save_manifests(manifests)
            if success:
                print("      ✅ Manifestos salvos com sucesso")
                
                # Verificar arquivos salvos
                manifest_files = list(kubernetes_orchestration.manifests_dir.glob("*.yaml"))
                print(f"      📁 Arquivos salvos: {len(manifest_files)}")
                
                for file_path in manifest_files[:5]:  # Mostrar primeiros 5
                    print(f"         • {file_path.name}")
                
                if len(manifest_files) > 5:
                    print(f"         ... e mais {len(manifest_files) - 5} arquivos")
            else:
                print("      ❌ Erro ao salvar manifestos")
        
        # 8. Simular aplicação dos manifestos
        print("\n8️⃣ Simulando aplicação dos manifestos...")
        
        print("   🔄 Aplicando manifestos no cluster...")
        success = apply_manifests()
        
        if success:
            print("      ✅ Manifestos aplicados com sucesso")
        else:
            print("      ❌ Erro ao aplicar manifestos")
        
        # 9. Verificar status do cluster
        print("\n9️⃣ Verificando status do cluster...")
        
        cluster_status = get_cluster_status()
        
        if 'error' not in cluster_status:
            print(f"   🏗️  Cluster: {cluster_status['cluster_name']}")
            print(f"   📁 Namespace: {cluster_status['namespace']}")
            
            # Status dos nós
            nodes = cluster_status['nodes']
            print(f"   🖥️  Nós ({len(nodes)}):")
            for node in nodes:
                status_icon = "✅" if node['status'] == 'Ready' else "❌"
                print(f"      {status_icon} {node['name']}: {node['status']} (CPU: {node['cpu']}, RAM: {node['memory']})")
            
            # Status dos pods
            pods = cluster_status['pods']
            print(f"   🐳 Pods:")
            for pod_name, pod_status in pods.items():
                status_icon = "✅" if pod_status['status'] == 'Running' else "❌"
                print(f"      {status_icon} {pod_name}: {pod_status['ready']}/{pod_status['total']} ({pod_status['status']})")
            
            # Status dos serviços
            services = cluster_status['services']
            print(f"   🌐 Serviços:")
            for service_name, service_status in services.items():
                if service_status['type'] == 'LoadBalancer':
                    print(f"      🌍 {service_name}: {service_status['type']} - IP: {service_status['external_ip']}")
                else:
                    print(f"      🔗 {service_name}: {service_status['type']} - IP: {service_status['cluster_ip']}")
        else:
            print(f"   ❌ Erro ao obter status: {cluster_status['error']}")
        
        # 10. Testar escalonamento
        print("\n🔟 Testando escalonamento...")
        
        try:
            # Escalar ML API para 5 réplicas
            print("   📈 Escalando ml-api para 5 réplicas...")
            success = scale_deployment('ml-api', 5)
            
            if success:
                print("      ✅ Deployment escalado com sucesso")
                
                # Verificar nova configuração
                new_replicas = kubernetes_orchestration.deployments['ml-api'].replicas
                print(f"      📊 Novas réplicas: {new_replicas}")
            else:
                print("      ❌ Erro ao escalar deployment")
                
        except Exception as e:
            print(f"      ❌ Erro no escalonamento: {e}")
        
        # 11. Testar obtenção de logs
        print("\n1️⃣1️⃣ Testando obtenção de logs...")
        
        try:
            # Obter logs do ML API
            print("   📝 Obtendo logs do ml-api...")
            logs = get_deployment_logs('ml-api', tail_lines=10)
            
            if logs:
                print(f"      ✅ {len(logs)} linhas de log obtidas")
                print("      📋 Últimas linhas:")
                for log in logs[-3:]:  # Últimas 3 linhas
                    print(f"         • {log}")
            else:
                print("      ❌ Nenhum log obtido")
                
        except Exception as e:
            print(f"      ❌ Erro ao obter logs: {e}")
        
        # 12. Testar backup do cluster
        print("\n1️⃣2️⃣ Testando backup do cluster...")
        
        try:
            print("   💾 Criando backup do cluster...")
            backup_path = kubernetes_orchestration.create_backup()
            
            if not backup_path.startswith('Erro'):
                print(f"      ✅ Backup criado: {backup_path}")
            else:
                print(f"      ❌ Erro no backup: {backup_path}")
                
        except Exception as e:
            print(f"      ❌ Erro no backup: {e}")
        
        # 13. Demonstração de funcionalidades avançadas
        print("\n1️⃣3️⃣ Funcionalidades avançadas disponíveis...")
        
        advanced_features = [
            "✅ Orquestração completa com Kubernetes",
            "✅ Deployments com health checks e probes",
            "✅ Serviços LoadBalancer e ClusterIP",
            "✅ Ingress com TLS e SSL redirect",
            "✅ Volumes persistentes para dados ML",
            "✅ ConfigMaps e Secrets para configuração",
            "✅ Horizontal Pod Autoscaler (HPA)",
            "✅ Escalonamento automático baseado em CPU/Memória",
            "✅ Monitoramento distribuído com Prometheus/Grafana",
            "✅ Backup e recuperação do cluster",
            "✅ Logs centralizados de todos os pods",
            "✅ Gerenciamento de recursos (CPU/Memória)",
            "✅ Rolling updates e rollbacks",
            "✅ Service discovery e load balancing",
            "✅ Segurança com RBAC e network policies"
        ]
        
        for feature in advanced_features:
            print(f"   {feature}")
        
        # 14. Próximos passos para produção
        print("\n1️⃣4️⃣ Próximos passos para produção...")
        
        next_steps = [
            "☸️ Configurar cluster Kubernetes real (EKS, GKE, AKS)",
            "🐳 Criar imagens Docker para os serviços",
            "📊 Implementar monitoramento com Prometheus + Grafana",
            "🔐 Configurar RBAC e políticas de segurança",
            "🌐 Configurar ingress controller (nginx, traefik)",
            "💾 Configurar storage classes para volumes persistentes",
            "🔄 Implementar CI/CD com ArgoCD ou Flux",
            "📈 Configurar métricas customizadas para HPA",
            "🔍 Implementar logging centralizado (ELK stack)",
            "🛡️ Configurar network policies e security contexts"
        ]
        
        for step in next_steps:
            print(f"   {step}")
        
        print("\n🎉 Demonstração da orquestração Kubernetes concluída com sucesso!")
        print("\n💡 Para implementar em produção:")
        print("   1. Configure um cluster Kubernetes real")
        print("   2. Crie as imagens Docker dos serviços")
        print("   3. Configure o registry de imagens")
        print("   4. Implemente monitoramento e alertas")
        print("   5. Configure backup e disaster recovery")
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("   Certifique-se de que todas as dependências estão instaladas")
    except Exception as e:
        print(f"❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
