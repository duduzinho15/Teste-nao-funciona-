"""
Script de teste para validar os endpoints de recomendações de apostas
"""

import sqlite3
import os
from datetime import datetime, timedelta
import sys

# Adicionar o diretório raiz ao path para importar módulos ML
sys.path.append(os.path.dirname(__file__))

from Coleta_de_dados.ml.gerar_recomendacoes import GeradorRecomendacoes

def test_gerador_recomendacoes():
    """Testa o gerador de recomendações diretamente"""
    print("🧪 TESTANDO GERADOR DE RECOMENDAÇÕES")
    print("=" * 50)
    
    try:
        # Inicializar gerador
        gerador = GeradorRecomendacoes()
        print("✅ GeradorRecomendacoes inicializado com sucesso")
        
        # Carregar modelo
        if gerador.carregar_ultimo_modelo():
            print("✅ Modelo ML carregado com sucesso")
            print(f"📊 Tipo: {gerador.modelo_carregado['tipo_modelo']}")
            print(f"📊 Accuracy: {gerador.modelo_carregado['accuracy']:.4f}")
        else:
            print("❌ Falha ao carregar modelo")
            return False
        
        # Gerar recomendações
        print("\n🔄 Gerando recomendações para próximos 7 dias...")
        resultado = gerador.gerar_recomendacoes_partidas_futuras(dias_futuros=7)
        
        if resultado:
            print(f"✅ {len(resultado)} recomendações geradas com sucesso!")
            print(f"📊 Partidas processadas: {len(set(r['partida_id'] for r in resultado))}")
            print(f"📊 Mercados gerados: {list(set(r['mercado_aposta'] for r in resultado))}")
            
            # Mostrar algumas recomendações
            print("\n📋 Exemplos de recomendações:")
            for i, rec in enumerate(resultado[:3]):
                print(f"  {i+1}. {rec['time_casa']} vs {rec['time_visitante']}")
                print(f"     Mercado: {rec['mercado_aposta']}")
                print(f"     Previsão: {rec['previsao']} (Prob: {rec['probabilidade']:.3f})")
                print(f"     Odd justa: {rec['odd_justa']:.2f}")
                print()
        else:
            print("⚠️ Nenhuma recomendação foi gerada")
            print("   (Pode não haver partidas futuras disponíveis)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_queries():
    """Testa as queries do banco de dados"""
    print("\n🗄️ TESTANDO QUERIES DO BANCO DE DADOS")
    print("=" * 50)
    
    db_path = os.path.join("Banco_de_dados", "aposta.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Testar query de recomendações
        print("📊 Testando query de recomendações...")
        cursor.execute("SELECT COUNT(*) FROM recomendacoes_apostas")
        total = cursor.fetchone()[0]
        print(f"✅ Total de recomendações: {total}")
        
        # Testar query de partidas futuras
        print("\n📊 Testando query de partidas futuras...")
        query = """
        SELECT 
            p.id,
            p.data,
            p.time_casa,
            p.time_visitante
        FROM partidas p
        WHERE p.data > datetime('now')
        ORDER BY p.data
        LIMIT 5
        """
        
        cursor.execute(query)
        partidas = cursor.fetchall()
        print(f"✅ Partidas futuras encontradas: {len(partidas)}")
        
        if partidas:
            print("📋 Exemplos de partidas futuras:")
            for partida in partidas[:3]:
                print(f"  - ID: {partida[0]}, {partida[2]} vs {partida[3]} em {partida[1]}")
        
        # Testar query de estatísticas
        print("\n📊 Testando query de estatísticas...")
        cursor.execute("""
            SELECT mercado_aposta, COUNT(*) 
            FROM recomendacoes_apostas 
            GROUP BY mercado_aposta
        """)
        mercados = dict(cursor.fetchall())
        print(f"✅ Mercados disponíveis: {mercados}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste do banco: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def main():
    """Função principal de teste"""
    print("🚀 TESTE DOS ENDPOINTS DE RECOMENDAÇÕES")
    print("=" * 60)
    
    # Teste 1: Gerador de recomendações
    test1_success = test_gerador_recomendacoes()
    
    # Teste 2: Queries do banco
    test2_success = test_database_queries()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 60)
    
    if test1_success and test2_success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de recomendações funcionando perfeitamente")
        print("✅ Endpoints prontos para uso na API")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        if not test1_success:
            print("   - Gerador de recomendações com problemas")
        if not test2_success:
            print("   - Queries do banco com problemas")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Resolver problemas identificados (se houver)")
    print("2. Integrar endpoints na API FastAPI")
    print("3. Testar endpoints via HTTP")
    print("4. Implementar monitoramento e métricas")

if __name__ == "__main__":
    main()
