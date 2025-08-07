#!/usr/bin/env python3
"""
VERIFICAÇÃO DE TABELAS FBREF - VERSÃO SQLAlchemy ORM
===================================================

Script refatorado para verificar tabelas do sistema FBRef usando SQLAlchemy ORM.
Substitui a versão SQLite direta pela nova arquitetura de banco de dados.

Funcionalidades:
- Verificação de conexão com banco de dados
- Listagem de todas as tabelas disponíveis
- Contagem de registros por tabela
- Verificação específica das tabelas FBRef
- Status do pool de conexões

Autor: Sistema de Migração de Banco de Dados
Data: 2025-08-03
Versão: 2.0 (ORM)
"""

import logging
from typing import Dict, List
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

# Imports do sistema de banco de dados
from Coleta_de_dados.database import db_manager, SessionLocal
from Coleta_de_dados.database.models import (
    Competicao, LinkParaColeta, Partida, EstatisticaPartida,
    PaisClube, Clube, EstatisticaClube, RecordVsOpponent,
    PaisJogador, Jogador, EstatisticaJogadorGeral, EstatisticaJogadorCompeticao
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FBRefTableVerifier:
    """Verificador de tabelas FBRef usando SQLAlchemy ORM."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Mapeamento de modelos ORM para nomes de tabelas
        self.fbref_models = {
            'competicoes': Competicao,
            'links_para_coleta': LinkParaColeta,
            'partidas': Partida,
            'estatisticas_partidas': EstatisticaPartida,
            'paises_clubes': PaisClube,
            'clubes': Clube,
            'estatisticas_clube': EstatisticaClube,
            'records_vs_opponents': RecordVsOpponent,
            'paises_jogadores': PaisJogador,
            'jogadores': Jogador,
            'estatisticas_jogador_geral': EstatisticaJogadorGeral,
            'estatisticas_jogador_competicao': EstatisticaJogadorCompeticao
        }
    
    def test_database_connection(self) -> bool:
        """Testa a conexão com o banco de dados."""
        self.logger.info("🔍 Testando conexão com banco de dados...")
        
        try:
            success = db_manager.test_connection()
            
            if success:
                self.logger.info("✅ Conexão estabelecida com sucesso!")
                
                # Mostrar status do pool
                pool_status = db_manager.get_pool_status()
                self.logger.info(f"📊 Status do pool: {pool_status}")
                
                return True
            else:
                self.logger.error("❌ Falha na conexão com banco de dados")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar conexão: {e}")
            return False
    
    def get_all_tables(self) -> List[str]:
        """Obtém lista de todas as tabelas no banco."""
        try:
            inspector = inspect(db_manager.engine)
            tables = inspector.get_table_names()
            return sorted(tables)
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter lista de tabelas: {e}")
            return []
    
    def count_records_in_table(self, session, model_class) -> int:
        """Conta registros em uma tabela usando ORM."""
        try:
            count = session.query(model_class).count()
            return count
        except Exception as e:
            self.logger.error(f"❌ Erro ao contar registros em {model_class.__tablename__}: {e}")
            return -1
    
    def verify_all_tables(self) -> Dict:
        """Verifica todas as tabelas disponíveis."""
        self.logger.info("📊 Verificando todas as tabelas disponíveis...")
        
        results = {
            "total_tables": 0,
            "tables": {},
            "errors": []
        }
        
        try:
            # Obter lista de tabelas
            tables = self.get_all_tables()
            results["total_tables"] = len(tables)
            
            if not tables:
                self.logger.warning("⚠️ Nenhuma tabela encontrada no banco")
                return results
            
            self.logger.info(f"📋 Total de tabelas encontradas: {len(tables)}")
            
            # Contar registros usando SQL direto para tabelas não mapeadas
            with SessionLocal() as session:
                for table_name in tables:
                    try:
                        result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        count = result.scalar()
                        results["tables"][table_name] = count
                        self.logger.info(f"✅ {table_name}: {count} registro(s)")
                    except Exception as e:
                        error_msg = f"Erro ao contar {table_name}: {e}"
                        results["errors"].append(error_msg)
                        self.logger.error(f"❌ {table_name}: ERRO - {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar tabelas: {e}")
            results["errors"].append(f"Erro geral: {e}")
            return results
    
    def verify_fbref_tables(self) -> Dict:
        """Verifica especificamente as tabelas do FBRef usando ORM."""
        self.logger.info("🎯 Verificando tabelas específicas do FBRef...")
        
        results = {
            "fbref_tables": {},
            "missing_tables": [],
            "errors": []
        }
        
        try:
            with SessionLocal() as session:
                for table_name, model_class in self.fbref_models.items():
                    try:
                        count = self.count_records_in_table(session, model_class)
                        
                        if count >= 0:
                            results["fbref_tables"][table_name] = count
                            self.logger.info(f"✅ {table_name}: {count} registro(s)")
                        else:
                            results["missing_tables"].append(table_name)
                            self.logger.warning(f"❌ {table_name}: Tabela não acessível")
                            
                    except Exception as e:
                        error_msg = f"Erro ao verificar {table_name}: {e}"
                        results["errors"].append(error_msg)
                        self.logger.error(f"❌ {table_name}: ERRO - {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar tabelas FBRef: {e}")
            results["errors"].append(f"Erro geral: {e}")
            return results
    
    def generate_summary_report(self, all_tables_result: Dict, fbref_tables_result: Dict):
        """Gera relatório resumido da verificação."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 RELATÓRIO RESUMIDO DA VERIFICAÇÃO")
        self.logger.info("=" * 60)
        
        # Estatísticas gerais
        total_tables = all_tables_result["total_tables"]
        total_records = sum(count for count in all_tables_result["tables"].values() if count > 0)
        
        self.logger.info(f"📋 Total de tabelas no banco: {total_tables}")
        self.logger.info(f"📊 Total de registros: {total_records:,}")
        
        # Tabelas FBRef
        fbref_count = len(fbref_tables_result["fbref_tables"])
        fbref_records = sum(fbref_tables_result["fbref_tables"].values())
        missing_count = len(fbref_tables_result["missing_tables"])
        
        self.logger.info(f"🎯 Tabelas FBRef encontradas: {fbref_count}")
        self.logger.info(f"📊 Registros FBRef: {fbref_records:,}")
        
        if missing_count > 0:
            self.logger.warning(f"⚠️ Tabelas FBRef faltando: {missing_count}")
            for table in fbref_tables_result["missing_tables"]:
                self.logger.warning(f"   - {table}")
        
        # Top 5 tabelas com mais registros
        if all_tables_result["tables"]:
            top_tables = sorted(
                all_tables_result["tables"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            self.logger.info("\n🏆 TOP 5 TABELAS COM MAIS REGISTROS:")
            for i, (table, count) in enumerate(top_tables, 1):
                self.logger.info(f"   {i}. {table}: {count:,} registros")
        
        # Erros encontrados
        total_errors = len(all_tables_result["errors"]) + len(fbref_tables_result["errors"])
        if total_errors > 0:
            self.logger.warning(f"\n⚠️ Total de erros encontrados: {total_errors}")
        else:
            self.logger.info("\n✅ Nenhum erro encontrado!")
        
        self.logger.info("=" * 60)
    
    def run_complete_verification(self) -> bool:
        """Executa verificação completa das tabelas."""
        self.logger.info("🚀 INICIANDO VERIFICAÇÃO COMPLETA DE TABELAS FBREF")
        self.logger.info("=" * 55)
        
        try:
            # Testar conexão
            if not self.test_database_connection():
                self.logger.error("❌ Falha na conexão - abortando verificação")
                return False
            
            # Verificar todas as tabelas
            self.logger.info("\n" + "-" * 40)
            all_tables_result = self.verify_all_tables()
            
            # Verificar tabelas FBRef específicas
            self.logger.info("\n" + "-" * 40)
            fbref_tables_result = self.verify_fbref_tables()
            
            # Gerar relatório resumido
            self.generate_summary_report(all_tables_result, fbref_tables_result)
            
            # Determinar sucesso
            has_errors = (len(all_tables_result["errors"]) + len(fbref_tables_result["errors"])) > 0
            has_fbref_tables = len(fbref_tables_result["fbref_tables"]) > 0
            
            if has_fbref_tables and not has_errors:
                self.logger.info("\n🎉 VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
                return True
            elif has_fbref_tables:
                self.logger.warning("\n⚠️ VERIFICAÇÃO CONCLUÍDA COM AVISOS")
                return True
            else:
                self.logger.error("\n❌ VERIFICAÇÃO FALHOU - PROBLEMAS CRÍTICOS")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro crítico na verificação: {e}")
            return False

def verificar_tabelas_fbref():
    """Função de compatibilidade com a versão anterior."""
    verifier = FBRefTableVerifier()
    return verifier.run_complete_verification()

def main():
    """Função principal."""
    print("🚀 VERIFICAÇÃO DE TABELAS FBREF - VERSÃO ORM")
    print("=" * 50)
    
    verifier = FBRefTableVerifier()
    
    try:
        success = verifier.run_complete_verification()
        
        if success:
            print("\n✅ VERIFICAÇÃO CONCLUÍDA!")
        else:
            print("\n❌ VERIFICAÇÃO COM PROBLEMAS!")
            
    except KeyboardInterrupt:
        print("\n⚠️ Verificação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
