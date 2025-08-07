#!/usr/bin/env python3
"""
Teste diagnóstico para identificar o problema na preparação do banco de dados.
"""
import sys
import os
import logging
import traceback
import sqlite3

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_database_creation():
    """Testa a criação do banco de dados com diagnóstico detalhado."""
    try:
        logger.info("=== TESTE DIAGNÓSTICO DO BANCO DE DADOS ===")
        
        # Teste 1: Verificar se o módulo pode ser importado
        logger.info("1. Testando importação do módulo criar_banco...")
        try:
            from Banco_de_dados.criar_banco import criar_todas_as_tabelas, DB_NAME
            logger.info("✅ Módulo importado com sucesso")
            logger.info(f"📁 Caminho do banco: {DB_NAME}")
        except Exception as e:
            logger.error(f"❌ Erro na importação: {e}")
            logger.error(traceback.format_exc())
            return False
        
        # Teste 2: Verificar se o diretório do banco existe
        logger.info("2. Verificando diretório do banco...")
        db_dir = os.path.dirname(DB_NAME)
        logger.info(f"📁 Diretório do banco: {db_dir}")
        
        if not os.path.exists(db_dir):
            logger.info(f"📁 Criando diretório: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
        
        logger.info(f"✅ Diretório existe: {os.path.exists(db_dir)}")
        
        # Teste 3: Testar conexão SQLite básica
        logger.info("3. Testando conexão SQLite básica...")
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            logger.info(f"✅ SQLite conectado, versão: {version}")
            conn.close()
        except Exception as e:
            logger.error(f"❌ Erro na conexão SQLite: {e}")
            return False
        
        # Teste 4: Executar criar_todas_as_tabelas com captura de erro
        logger.info("4. Executando criar_todas_as_tabelas...")
        try:
            resultado = criar_todas_as_tabelas()
            logger.info(f"✅ Função executada, resultado: {resultado}")
            
            # Verificar se o banco foi criado
            if os.path.exists(DB_NAME):
                logger.info("✅ Arquivo do banco foi criado")
                
                # Verificar algumas tabelas
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                logger.info(f"📊 Tabelas criadas: {len(tables)}")
                
                for table in tables[:10]:  # Mostrar apenas as primeiras 10
                    logger.info(f"  - {table[0]}")
                
                if len(tables) > 10:
                    logger.info(f"  ... e mais {len(tables) - 10} tabelas")
                
                conn.close()
                
                if len(tables) > 0:
                    logger.info("✅ BANCO CRIADO COM SUCESSO!")
                    return True
                else:
                    logger.error("❌ Banco criado mas sem tabelas")
                    return False
            else:
                logger.error("❌ Arquivo do banco não foi criado")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar criar_todas_as_tabelas: {e}")
            logger.error(f"📋 Traceback completo:")
            logger.error(traceback.format_exc())
            return False
    
    except Exception as e:
        logger.error(f"❌ Erro geral no teste: {e}")
        logger.error(traceback.format_exc())
        return False

def test_database_in_fallback_context():
    """Testa a criação do banco no contexto do sistema de fallback."""
    try:
        logger.info("\n=== TESTE NO CONTEXTO DO SISTEMA DE FALLBACK ===")
        
        from Coleta_de_dados.apis.fbref.fbref_fallback_system import create_fallback_system
        
        logger.info("1. Criando sistema de fallback...")
        fallback_system = create_fallback_system(PROJECT_ROOT)
        
        logger.info("2. Verificando status do banco...")
        db_status = fallback_system.check_database_status()
        
        logger.info("📊 Status do banco:")
        for key, value in db_status.items():
            logger.info(f"  - {key}: {value}")
        
        if db_status['database_exists']:
            logger.info("✅ Banco existe no contexto de fallback")
            return True
        else:
            logger.warning("⚠️ Banco não existe no contexto de fallback")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste de fallback: {e}")
        logger.error(traceback.format_exc())
        return False

def test_orchestrator_database_step():
    """Testa especificamente a etapa de preparação do banco no orquestrador."""
    try:
        logger.info("\n=== TESTE DA ETAPA DE PREPARAÇÃO NO ORQUESTRADOR ===")
        
        from Coleta_de_dados.apis.fbref.orquestrador_coleta import OrquestradorColeta
        
        logger.info("1. Criando orquestrador...")
        orquestrador = OrquestradorColeta()
        
        logger.info("2. Executando apenas a etapa de preparação do banco...")
        try:
            resultado = orquestrador._executar_preparacao_banco()
            logger.info(f"✅ Etapa executada, resultado: {resultado}")
            return resultado is not False
        except Exception as e:
            logger.error(f"❌ Erro na etapa de preparação: {e}")
            logger.error(traceback.format_exc())
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste do orquestrador: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("🔍 DIAGNÓSTICO COMPLETO DO PROBLEMA DO BANCO DE DADOS")
    logger.info("="*60)
    
    # Executa todos os testes
    test1_success = test_database_creation()
    test2_success = test_database_in_fallback_context()
    test3_success = test_orchestrator_database_step()
    
    # Resumo final
    logger.info("\n" + "="*60)
    logger.info("📋 RESUMO DO DIAGNÓSTICO:")
    logger.info(f"  1. Criação direta do banco: {'✅ SUCESSO' if test1_success else '❌ FALHA'}")
    logger.info(f"  2. Banco no contexto fallback: {'✅ SUCESSO' if test2_success else '❌ FALHA'}")
    logger.info(f"  3. Etapa do orquestrador: {'✅ SUCESSO' if test3_success else '❌ FALHA'}")
    
    if all([test1_success, test2_success, test3_success]):
        logger.info("\n🎉 TODOS OS TESTES PASSARAM! O problema pode estar em outro lugar.")
    else:
        logger.info("\n🔧 PROBLEMAS IDENTIFICADOS - vamos investigar mais...")
        
        if not test1_success:
            logger.info("  - Problema na criação básica do banco")
        if not test2_success:
            logger.info("  - Problema no contexto de fallback")  
        if not test3_success:
            logger.info("  - Problema na etapa do orquestrador")
