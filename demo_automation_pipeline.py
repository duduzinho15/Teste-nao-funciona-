#!/usr/bin/env python3
"""
Demonstração do Pipeline de Automação CI/CD
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
    print("🚀 APOSTAPRO - Demonstração do Pipeline de Automação CI/CD")
    print("=" * 80)
    
    try:
        # Importar módulos
        from ml_models.automation_pipeline import (
            automation_pipeline,
            run_pipeline,
            get_pipeline_status,
            schedule_pipeline,
            enable_pipeline
        )
        
        print("✅ Módulos importados com sucesso")
        
        # 1. Verificar configuração dos pipelines
        print("\n1️⃣ Verificando configuração dos pipelines...")
        
        pipeline_configs = automation_pipeline.pipelines
        print(f"   📊 Total de pipelines configurados: {len(pipeline_configs)}")
        
        for name, config in pipeline_configs.items():
            status = "✅ Habilitado" if config.enabled else "❌ Desabilitado"
            trigger = config.trigger_type
            schedule = config.schedule if config.trigger_type == 'schedule' else 'Manual'
            print(f"   • {name}: {status} | Trigger: {trigger} | Schedule: {schedule}")
        
        # 2. Verificar status atual dos pipelines
        print("\n2️⃣ Verificando status atual dos pipelines...")
        
        status = get_pipeline_status()
        if 'error' not in status:
            for pipeline_name, pipeline_status in status.items():
                total_runs = pipeline_status['total_runs']
                successful_runs = pipeline_status['successful_runs']
                failed_runs = pipeline_status['failed_runs']
                
                print(f"   📈 {pipeline_name}:")
                print(f"      - Total de execuções: {total_runs}")
                print(f"      - Sucessos: {successful_runs}")
                print(f"      - Falhas: {failed_runs}")
                
                if pipeline_status['last_run']:
                    last_run = pipeline_status['last_run']
                    last_status = last_run['status']
                    last_time = last_run['start_time']
                    print(f"      - Última execução: {last_time} ({last_status})")
        else:
            print(f"   ❌ Erro ao obter status: {status['error']}")
        
        # 3. Executar pipeline de treinamento ML
        print("\n3️⃣ Executando pipeline de treinamento ML...")
        
        try:
            print("   🔄 Iniciando pipeline...")
            run_id = run_pipeline('ml_training', 'manual')
            print(f"      ✅ Pipeline iniciado com ID: {run_id}")
            
            # Aguardar um pouco para simular execução
            import time
            print("      ⏳ Aguardando execução...")
            time.sleep(3)
            
            # Verificar status
            training_status = get_pipeline_status('ml_training')
            if 'error' not in training_status and training_status['last_run']:
                last_run = training_status['last_run']
                print(f"      📊 Status: {last_run['status']}")
                print(f"      ⏱️  Duração: {last_run['start_time']} a {last_run['end_time']}")
                print(f"      ✅ Passos completados: {len(last_run['steps_completed'])}")
                if last_run['steps_failed']:
                    print(f"      ❌ Passos falharam: {len(last_run['steps_failed'])}")
                
                # Mostrar logs
                print("      📝 Logs da execução:")
                for log in last_run['logs'][:5]:  # Primeiros 5 logs
                    print(f"         • {log}")
                
                # Mostrar artefatos
                if last_run['artifacts']:
                    print("      🎁 Artefatos gerados:")
                    for artifact in last_run['artifacts']:
                        print(f"         • {artifact}")
            
        except Exception as e:
            print(f"      ❌ Erro ao executar pipeline: {e}")
        
        # 4. Executar pipeline de monitoramento de performance
        print("\n4️⃣ Executando pipeline de monitoramento de performance...")
        
        try:
            print("   🔄 Iniciando pipeline...")
            run_id = run_pipeline('performance_monitoring', 'manual')
            print(f"      ✅ Pipeline iniciado com ID: {run_id}")
            
            # Aguardar execução
            print("      ⏳ Aguardando execução...")
            time.sleep(2)
            
            # Verificar status
            monitoring_status = get_pipeline_status('performance_monitoring')
            if 'error' not in monitoring_status and monitoring_status['last_run']:
                last_run = monitoring_status['last_run']
                print(f"      📊 Status: {last_run['status']}")
                print(f"      ✅ Passos completados: {len(last_run['steps_completed'])}")
                
        except Exception as e:
            print(f"      ❌ Erro ao executar pipeline: {e}")
        
        # 5. Executar pipeline de validação de dados
        print("\n5️⃣ Executando pipeline de validação de dados...")
        
        try:
            print("   🔄 Iniciando pipeline...")
            run_id = run_pipeline('data_validation', 'manual')
            print(f"      ✅ Pipeline iniciado com ID: {run_id}")
            
            # Aguardar execução
            print("      ⏳ Aguardando execução...")
            time.sleep(2)
            
            # Verificar status
            validation_status = get_pipeline_status('data_validation')
            if 'error' not in validation_status and validation_status['last_run']:
                last_run = validation_status['last_run']
                print(f"      📊 Status: {last_run['status']}")
                print(f"      ✅ Passos completados: {len(last_run['steps_completed'])}")
                
        except Exception as e:
            print(f"      ❌ Erro ao executar pipeline: {e}")
        
        # 6. Testar agendamento de pipelines
        print("\n6️⃣ Testando agendamento de pipelines...")
        
        try:
            # Agendar pipeline de treinamento para executar a cada hora
            new_schedule = "0 * * * *"  # A cada hora
            success = schedule_pipeline('ml_training', new_schedule)
            
            if success:
                print(f"      ✅ Pipeline ml_training agendado: {new_schedule}")
                
                # Verificar novo agendamento
                updated_config = automation_pipeline.pipelines['ml_training']
                print(f"      📅 Novo schedule: {updated_config.schedule}")
            else:
                print("      ❌ Erro ao agendar pipeline")
                
        except Exception as e:
            print(f"      ❌ Erro no agendamento: {e}")
        
        # 7. Testar habilitação/desabilitação de pipelines
        print("\n7️⃣ Testando controle de pipelines...")
        
        try:
            # Desabilitar pipeline de validação de dados
            success = enable_pipeline('data_validation', False)
            
            if success:
                print("      ✅ Pipeline data_validation desabilitado")
                
                # Verificar status
                updated_config = automation_pipeline.pipelines['data_validation']
                print(f"      📊 Status: {'Habilitado' if updated_config.enabled else 'Desabilitado'}")
                
                # Reabilitar
                enable_pipeline('data_validation', True)
                print("      ✅ Pipeline data_validation reabilitado")
            else:
                print("      ❌ Erro ao alterar status do pipeline")
                
        except Exception as e:
            print(f"      ❌ Erro no controle: {e}")
        
        # 8. Verificar status final
        print("\n8️⃣ Status final dos pipelines...")
        
        final_status = get_pipeline_status()
        if 'error' not in final_status:
            total_executions = sum(status['total_runs'] for status in final_status.values())
            total_successes = sum(status['successful_runs'] for status in final_status.values())
            total_failures = sum(status['failed_runs'] for status in final_status.values())
            
            print(f"   📊 Resumo geral:")
            print(f"      - Total de execuções: {total_executions}")
            print(f"      - Sucessos: {total_successes}")
            print(f"      - Falhas: {total_failures}")
            
            if total_executions > 0:
                success_rate = (total_successes / total_executions) * 100
                print(f"      - Taxa de sucesso: {success_rate:.1f}%")
        
        # 9. Demonstração de funcionalidades avançadas
        print("\n9️⃣ Funcionalidades avançadas disponíveis...")
        
        advanced_features = [
            "✅ Pipeline de treinamento ML automatizado",
            "✅ Pipeline de deploy com rollback automático",
            "✅ Monitoramento contínuo de performance",
            "✅ Validação automática de dados",
            "✅ Agendamento com expressões cron",
            "✅ Notificações por email e Slack",
            "✅ Versionamento automático de modelos",
            "✅ Backup automático antes do deploy",
            "✅ Testes automatizados pós-treinamento",
            "✅ Coleta e análise de métricas",
            "✅ Detecção automática de anomalias",
            "✅ Limpeza automática de dados",
            "✅ Histórico completo de execuções",
            "✅ Logs detalhados de cada passo",
            "✅ Artefatos persistentes"
        ]
        
        for feature in advanced_features:
            print(f"   {feature}")
        
        # 10. Próximos passos para produção
        print("\n🔟 Próximos passos para produção...")
        
        next_steps = [
            "🌐 Integrar com sistemas de CI/CD (Jenkins, GitLab CI, GitHub Actions)",
            "🐳 Containerização com Docker para portabilidade",
            "☸️ Orquestração com Kubernetes para escalabilidade",
            "📊 Dashboard para monitoramento de pipelines",
            "🔐 Autenticação e autorização de usuários",
            "📧 Configuração de notificações reais",
            "💾 Integração com sistemas de versionamento (Git)",
            "🧪 Testes unitários e de integração",
            "📈 Métricas de performance dos pipelines",
            "🔄 Implementar retry automático com backoff exponencial"
        ]
        
        for step in next_steps:
            print(f"   {step}")
        
        print("\n🎉 Demonstração do pipeline de automação concluída com sucesso!")
        print("\n💡 Para implementar em produção:")
        print("   1. Configure as notificações reais (email, Slack)")
        print("   2. Integre com sistemas de CI/CD existentes")
        print("   3. Implemente autenticação e controle de acesso")
        print("   4. Configure monitoramento e alertas")
        print("   5. Implemente backup e recuperação de desastres")
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("   Certifique-se de que todas as dependências estão instaladas")
    except Exception as e:
        print(f"❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
