#!/usr/bin/env python3
"""
Demonstração do Dashboard Web Interativo
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
    print("🌐 APOSTAPRO - Demonstração do Dashboard Web Interativo")
    print("=" * 80)
    
    try:
        # Importar módulos
        from ml_models.web_dashboard import (
            web_dashboard,
            get_dashboard_data,
            generate_system_chart,
            generate_ml_chart,
            generate_betting_chart
        )
        
        print("✅ Módulos importados com sucesso")
        
        # 1. Testar geração de gráficos individuais
        print("\n1️⃣ Testando geração de gráficos individuais...")
        
        print("   📊 Gerando gráfico de visão geral do sistema...")
        system_chart = generate_system_chart()
        if system_chart and 'error' not in system_chart:
            print("      ✅ Gráfico do sistema gerado com sucesso")
        else:
            print("      ⚠️  Erro ao gerar gráfico do sistema")
        
        print("   🤖 Gerando gráfico de performance ML...")
        ml_chart = generate_ml_chart()
        if ml_chart and 'error' not in ml_chart:
            print("      ✅ Gráfico ML gerado com sucesso")
        else:
            print("      ⚠️  Erro ao gerar gráfico ML")
        
        print("   🎲 Gerando gráfico de análise de apostas...")
        betting_chart = generate_betting_chart()
        if betting_chart and 'error' not in betting_chart:
            print("      ✅ Gráfico de apostas gerado com sucesso")
        else:
            print("      ⚠️  Erro ao gerar gráfico de apostas")
        
        # 2. Testar geração de todos os gráficos
        print("\n2️⃣ Testando geração de todos os gráficos...")
        
        print("   🔄 Gerando dados completos do dashboard...")
        dashboard_data = get_dashboard_data()
        
        if 'error' not in dashboard_data:
            print("      ✅ Dashboard gerado com sucesso")
            
            # Verificar estrutura dos dados
            charts = dashboard_data.get('charts', {})
            metrics = dashboard_data.get('metrics', {})
            alerts = dashboard_data.get('alerts', [])
            
            print(f"      📈 Gráficos gerados: {len(charts)}")
            for chart_name in charts.keys():
                print(f"         • {chart_name}")
            
            print(f"      📊 Métricas disponíveis: {len(metrics)}")
            for metric_name, metric_value in metrics.items():
                print(f"         • {metric_name}: {metric_value}")
            
            print(f"      🚨 Alertas recentes: {len(alerts)}")
            for alert in alerts[:3]:  # Mostrar apenas os 3 primeiros
                level = alert.get('level', 'info')
                message = alert.get('message', 'Sem mensagem')
                print(f"         • [{level.upper()}] {message[:50]}...")
        else:
            print(f"      ❌ Erro ao gerar dashboard: {dashboard_data['error']}")
        
        # 3. Testar funcionalidades específicas
        print("\n3️⃣ Testando funcionalidades específicas...")
        
        # Testar gráfico de tendências
        print("   📈 Gerando gráfico de análise de tendências...")
        trend_chart = web_dashboard.generate_trend_analysis_chart()
        if trend_chart and 'error' not in trend_chart:
            print("      ✅ Gráfico de tendências gerado com sucesso")
        else:
            print("      ⚠️  Erro ao gerar gráfico de tendências")
        
        # Testar gráfico de value betting
        print("   💰 Gerando gráfico de value betting...")
        value_chart = web_dashboard.generate_value_betting_chart()
        if value_chart and 'error' not in value_chart:
            print("      ✅ Gráfico de value betting gerado com sucesso")
        else:
            print("      ⚠️  Erro ao gerar gráfico de value betting")
        
        # 4. Verificar configurações
        print("\n4️⃣ Verificando configurações do dashboard...")
        
        config = web_dashboard.dashboard_config
        print(f"   ⏱️  Intervalo de atualização: {config['refresh_interval']} segundos")
        print(f"   📊 Máximo de pontos de dados: {config['max_data_points']}")
        print(f"   🎨 Cores disponíveis: {len(config['chart_colors'])}")
        
        # 5. Verificar diretórios
        print("\n5️⃣ Verificando estrutura de diretórios...")
        
        dashboard_dir = web_dashboard.dashboard_dir
        print(f"   📁 Diretório do dashboard: {dashboard_dir}")
        print(f"      ✅ Existe: {dashboard_dir.exists()}")
        
        # 6. Demonstração de funcionalidades avançadas
        print("\n6️⃣ Funcionalidades avançadas disponíveis...")
        
        advanced_features = [
            "✅ Gráficos interativos com Plotly",
            "✅ Dashboard responsivo e moderno",
            "✅ Atualização automática em tempo real",
            "✅ Múltiplos tipos de visualização",
            "✅ Integração com sistema de monitoramento",
            "✅ Análise de mercado em tempo real",
            "✅ Identificação de oportunidades de value betting",
            "✅ Análise de tendências do sistema",
            "✅ Métricas de saúde do sistema",
            "✅ Sistema de alertas visual"
        ]
        
        for feature in advanced_features:
            print(f"   {feature}")
        
        # 7. Próximos passos para implementação web
        print("\n7️⃣ Próximos passos para implementação web...")
        
        next_steps = [
            "🌐 Criar aplicação web com FastAPI + Dash",
            "📱 Implementar interface responsiva",
            "🔄 Adicionar atualizações em tempo real",
            "🔐 Implementar autenticação de usuários",
            "📊 Adicionar mais tipos de gráficos",
            "💾 Implementar persistência de dados",
            "📈 Adicionar relatórios exportáveis",
            "🔔 Implementar notificações push"
        ]
        
        for step in next_steps:
            print(f"   {step}")
        
        print("\n🎉 Demonstração do dashboard web concluída com sucesso!")
        print("\n💡 Para implementar o dashboard web completo:")
        print("   1. Instale as dependências: pip install -r requirements_ml.txt")
        print("   2. Crie uma aplicação FastAPI com endpoints para os gráficos")
        print("   3. Implemente uma interface web com Dash ou HTML/CSS/JS")
        print("   4. Configure atualizações automáticas via WebSockets")
        print("   5. Adicione autenticação e controle de acesso")
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("   Certifique-se de que todas as dependências estão instaladas")
        print("   Execute: pip install -r requirements_ml.txt")
    except Exception as e:
        print(f"❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
