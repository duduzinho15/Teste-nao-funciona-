#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do sistema FBRef.
Testa cada módulo individualmente para garantir que está funcionando.
"""

import sys
import os
import logging
from datetime import datetime

# Adiciona o diretório raiz ao path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
)
logger = logging.getLogger(__name__)

def testar_importacoes():
    """Testa se todos os módulos podem ser importados."""
    logger.info("🔍 Testando importações...")
    
    try:
        from Coleta_de_dados.apis.fbref.fbref_integrado import main as descobrir_links
        from Coleta_de_dados.apis.fbref.coletar_dados_partidas import main as coletar_partidas
        from Coleta_de_dados.apis.fbref.coletar_estatisticas_detalhadas import main as coletar_estatisticas
        from Coleta_de_dados.apis.fbref.verificar_extracao import VerificadorExtracao
        from Coleta_de_dados.apis.fbref.coletar_clubes import ColetorClubes
        from Coleta_de_dados.apis.fbref.coletar_jogadores import ColetorJogadores
        from Coleta_de_dados.apis.fbref.orquestrador_coleta import OrquestradorColeta
        
        logger.info("✅ Todas as importações funcionaram!")
        return True
    except ImportError as e:
        logger.error(f"❌ Erro na importação: {e}")
        return False

def testar_banco_dados():
    """Testa se o banco de dados pode ser criado."""
    logger.info("🗄️ Testando criação do banco de dados...")
    
    try:
        from Banco_de_dados.criar_banco import criar_todas_as_tabelas
        criar_todas_as_tabelas()
        logger.info("✅ Banco de dados criado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao criar banco de dados: {e}")
        return False

def testar_descoberta_links():
    """Testa a descoberta de links (apenas algumas competições)."""
    logger.info("🔗 Testando descoberta de links...")
    
    try:
        from Coleta_de_dados.apis.fbref.fbref_integrado import coletar_competicoes
        
        competicoes = coletar_competicoes()
        if competicoes:
            logger.info(f"✅ Encontradas {len(competicoes)} competições")
            # Mostra algumas competições como exemplo
            for i, comp in enumerate(competicoes[:5]):
                logger.info(f"  {i+1}. {comp['nome']} ({comp['contexto']})")
            return True
        else:
            logger.warning("⚠️ Nenhuma competição encontrada")
            return False
    except Exception as e:
        logger.error(f"❌ Erro na descoberta de links: {e}")
        return False

def testar_verificacao_extracao():
    """Testa o sistema de verificação de extração."""
    logger.info("🔍 Testando sistema de verificação...")
    
    try:
        from Coleta_de_dados.apis.fbref.verificar_extracao import VerificadorExtracao
        
        verificador = VerificadorExtracao()
        stats = verificador.executar_verificacao_completa()
        
        logger.info(f"✅ Verificação concluída:")
        logger.info(f"  - Competições verificadas: {stats['competicoes_verificadas']}")
        logger.info(f"  - Competições completas: {stats['competicoes_completas']}")
        logger.info(f"  - Competições incompletas: {stats['competicoes_incompletas']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro na verificação: {e}")
        return False

def testar_coleta_clubes():
    """Testa a coleta de clubes (apenas alguns países)."""
    logger.info("🏟️ Testando coleta de clubes...")
    
    try:
        from Coleta_de_dados.apis.fbref.coletar_clubes import ColetorClubes
        
        coletor = ColetorClubes()
        coletor.setup_database_clubes()
        
        # Testa apenas com alguns países para não sobrecarregar
        paises = coletor.coletar_paises_clubes()
        if paises:
            logger.info(f"✅ Encontrados {len(paises)} países")
            # Testa com o primeiro país
            if len(paises) > 0:
                pais_teste = paises[0]
                clubes = coletor.coletar_clubes_do_pais(pais_teste)
                logger.info(f"✅ Encontrados {len(clubes)} clubes em {pais_teste.nome}")
                return True
        else:
            logger.warning("⚠️ Nenhum país encontrado")
            return False
    except Exception as e:
        logger.error(f"❌ Erro na coleta de clubes: {e}")
        return False

def testar_coleta_jogadores():
    """Testa a coleta de jogadores (apenas alguns países)."""
    logger.info("⚽ Testando coleta de jogadores...")
    
    try:
        from Coleta_de_dados.apis.fbref.coletar_jogadores import ColetorJogadores
        
        coletor = ColetorJogadores()
        coletor.setup_database_jogadores()
        
        # Testa apenas com alguns países para não sobrecarregar
        paises = coletor.coletar_paises_jogadores()
        if paises:
            logger.info(f"✅ Encontrados {len(paises)} países")
            # Testa com o primeiro país
            if len(paises) > 0:
                pais_teste = paises[0]
                jogadores = coletor.coletar_jogadores_do_pais(pais_teste)
                logger.info(f"✅ Encontrados {len(jogadores)} jogadores em {pais_teste.nome}")
                return True
        else:
            logger.warning("⚠️ Nenhum país encontrado")
            return False
    except Exception as e:
        logger.error(f"❌ Erro na coleta de jogadores: {e}")
        return False

def testar_orquestrador():
    """Testa o orquestrador (apenas listagem de etapas)."""
    logger.info("🎼 Testando orquestrador...")
    
    try:
        from Coleta_de_dados.apis.fbref.orquestrador_coleta import OrquestradorColeta
        
        orquestrador = OrquestradorColeta()
        orquestrador.listar_etapas()
        
        logger.info("✅ Orquestrador funcionando!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro no orquestrador: {e}")
        return False

def executar_testes_completos():
    """Executa todos os testes."""
    logger.info("🚀 Iniciando testes completos do sistema FBRef...")
    logger.info("="*80)
    
    testes = [
        ("Importações", testar_importacoes),
        ("Banco de Dados", testar_banco_dados),
        ("Descoberta de Links", testar_descoberta_links),
        ("Verificação de Extração", testar_verificacao_extracao),
        ("Coleta de Clubes", testar_coleta_clubes),
        ("Coleta de Jogadores", testar_coleta_jogadores),
        ("Orquestrador", testar_orquestrador),
    ]
    
    resultados = {}
    
    for nome_teste, funcao_teste in testes:
        logger.info(f"\n📋 Executando teste: {nome_teste}")
        try:
            sucesso = funcao_teste()
            resultados[nome_teste] = sucesso
            if sucesso:
                logger.info(f"✅ {nome_teste}: PASSOU")
            else:
                logger.warning(f"⚠️ {nome_teste}: FALHOU")
        except Exception as e:
            logger.error(f"❌ {nome_teste}: ERRO - {e}")
            resultados[nome_teste] = False
    
    # Relatório final
    logger.info("\n" + "="*80)
    logger.info("📊 RELATÓRIO FINAL DOS TESTES")
    logger.info("="*80)
    
    testes_passaram = sum(1 for resultado in resultados.values() if resultado)
    total_testes = len(resultados)
    
    for nome_teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        logger.info(f"  {status} | {nome_teste}")
    
    logger.info(f"\n📈 Resultado: {testes_passaram}/{total_testes} testes passaram")
    
    if testes_passaram == total_testes:
        logger.info("🎉 Todos os testes passaram! Sistema funcionando perfeitamente.")
    elif testes_passaram >= total_testes * 0.7:
        logger.warning("⚠️ Maioria dos testes passou. Alguns ajustes podem ser necessários.")
    else:
        logger.error("❌ Muitos testes falharam. Verifique o sistema.")
    
    logger.info("="*80)
    
    return resultados

if __name__ == "__main__":
    resultados = executar_testes_completos()
    
    # Retorna código de saída baseado nos resultados
    testes_passaram = sum(1 for resultado in resultados.values() if resultado)
    total_testes = len(resultados)
    
    if testes_passaram == total_testes:
        sys.exit(0)  # Sucesso
    else:
        sys.exit(1)  # Falha 