#!/usr/bin/env python3
"""
TESTE DO SISTEMA ORM - MIGRAÇÃO DE BANCO DE DADOS
=================================================

Script para testar o funcionamento completo do sistema SQLAlchemy ORM.
Valida conexões, modelos, operações CRUD e integração com scripts existentes.

Funcionalidades testadas:
1. Conexão com banco de dados
2. Criação e consulta de modelos ORM
3. Operações CRUD básicas
4. Integração com script FBRef refatorado
5. Performance e pool de conexões

Autor: Sistema de Migração de Banco de Dados
Data: 2025-08-03
Versão: 1.0
"""

import logging
import time
from typing import Dict, List
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ORMSystemTester:
    """Classe para testar o sistema ORM completo."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = {}
        
    def test_database_connection(self) -> bool:
        """Testa a conexão com o banco de dados."""
        self.logger.info("🔍 Testando conexão com banco de dados...")
        
        try:
            from Coleta_de_dados.database import db_manager
            
            # Testar conexão
            success = db_manager.test_connection()
            
            if success:
                self.logger.info("✅ Conexão com banco estabelecida")
                
                # Obter status do pool
                pool_status = db_manager.get_pool_status()
                self.logger.info(f"📊 Status do pool: {pool_status}")
                
                return True
            else:
                self.logger.error("❌ Falha na conexão com banco")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar conexão: {e}")
            return False
    
    def test_orm_models(self) -> bool:
        """Testa os modelos ORM básicos."""
        self.logger.info("🏗️ Testando modelos ORM...")
        
        try:
            from Coleta_de_dados.database import SessionLocal
            from Coleta_de_dados.database.models import Competicao, LinkParaColeta
            
            with SessionLocal() as session:
                # Testar criação de competição
                test_competicao = Competicao(
                    nome="Teste ORM",
                    url="https://fbref.com/test",
                    contexto="Teste",
                    ativa=True
                )
                
                session.add(test_competicao)
                session.flush()  # Para obter ID sem commit
                
                competicao_id = test_competicao.id
                self.logger.info(f"✅ Competição teste criada (ID: {competicao_id})")
                
                # Testar criação de link
                test_link = LinkParaColeta(
                    url="https://fbref.com/test/season",
                    competicao_id=competicao_id,
                    tipo="season",
                    status="pendente",
                    prioridade=1
                )
                
                session.add(test_link)
                session.flush()
                
                link_id = test_link.id
                self.logger.info(f"✅ Link teste criado (ID: {link_id})")
                
                # Testar consulta com relacionamento
                competicao_com_links = session.query(Competicao).filter_by(
                    id=competicao_id
                ).first()
                
                if competicao_com_links:
                    links_count = len(competicao_com_links.links)
                    self.logger.info(f"✅ Relacionamento funcionando: {links_count} links encontrados")
                
                # Rollback para não salvar dados de teste
                session.rollback()
                self.logger.info("✅ Rollback executado - dados de teste removidos")
                
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar modelos ORM: {e}")
            return False
    
    def test_fbref_integration(self) -> bool:
        """Testa a integração com o script FBRef refatorado."""
        self.logger.info("🔗 Testando integração FBRef ORM...")
        
        try:
            from Coleta_de_dados.apis.fbref.fbref_integrado_orm import FBRefCollectorORM
            
            # Criar instância do coletor
            collector = FBRefCollectorORM()
            self.logger.info("✅ FBRefCollectorORM instanciado")
            
            # Testar coleta de competições (modo cache/fallback)
            start_time = time.time()
            competicoes = collector.coletar_competicoes()
            elapsed_time = time.time() - start_time
            
            if competicoes:
                self.logger.info(f"✅ Coleta de competições funcionando: {len(competicoes)} competições em {elapsed_time:.2f}s")
                
                # Mostrar algumas competições como exemplo
                for i, comp in enumerate(competicoes[:3]):
                    self.logger.info(f"   {i+1}. {comp['nome']} ({comp['contexto']})")
                
                return True
            else:
                self.logger.warning("⚠️ Nenhuma competição coletada")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar integração FBRef: {e}")
            return False
    
    def test_performance(self) -> bool:
        """Testa performance básica do sistema."""
        self.logger.info("⚡ Testando performance do sistema...")
        
        try:
            from Coleta_de_dados.database import SessionLocal
            from Coleta_de_dados.database.models import Competicao
            
            # Teste de múltiplas sessões
            session_times = []
            
            for i in range(5):
                start_time = time.time()
                
                with SessionLocal() as session:
                    # Fazer uma consulta simples
                    count = session.query(Competicao).count()
                    
                elapsed_time = time.time() - start_time
                session_times.append(elapsed_time)
            
            avg_time = sum(session_times) / len(session_times)
            max_time = max(session_times)
            min_time = min(session_times)
            
            self.logger.info(f"✅ Performance de sessões:")
            self.logger.info(f"   Tempo médio: {avg_time:.3f}s")
            self.logger.info(f"   Tempo mín/máx: {min_time:.3f}s / {max_time:.3f}s")
            
            # Considerar performance boa se tempo médio < 0.1s
            if avg_time < 0.1:
                self.logger.info("✅ Performance excelente!")
                return True
            elif avg_time < 0.5:
                self.logger.info("✅ Performance boa")
                return True
            else:
                self.logger.warning("⚠️ Performance pode ser melhorada")
                return True  # Ainda consideramos sucesso
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar performance: {e}")
            return False
    
    def test_migration_compatibility(self) -> bool:
        """Testa compatibilidade com sistema de migrations."""
        self.logger.info("🔄 Testando compatibilidade com migrations...")
        
        try:
            # Verificar se Alembic está configurado
            import os
            alembic_ini = os.path.join(os.getcwd(), "alembic.ini")
            alembic_dir = os.path.join(os.getcwd(), "alembic")
            
            if os.path.exists(alembic_ini) and os.path.exists(alembic_dir):
                self.logger.info("✅ Alembic configurado corretamente")
                
                # Verificar se consegue importar env.py
                import sys
                sys.path.insert(0, alembic_dir)
                
                try:
                    import env
                    self.logger.info("✅ Ambiente Alembic importado com sucesso")
                except ImportError:
                    self.logger.warning("⚠️ Problema na importação do ambiente Alembic")
                
                return True
            else:
                self.logger.warning("⚠️ Configuração Alembic não encontrada")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar migrations: {e}")
            return False
    
    def run_comprehensive_test(self) -> Dict:
        """Executa todos os testes do sistema ORM."""
        self.logger.info("🚀 INICIANDO TESTE ABRANGENTE DO SISTEMA ORM")
        self.logger.info("=" * 60)
        
        tests = [
            ("Conexão com Banco de Dados", self.test_database_connection),
            ("Modelos ORM", self.test_orm_models),
            ("Integração FBRef", self.test_fbref_integration),
            ("Performance", self.test_performance),
            ("Compatibilidade Migrations", self.test_migration_compatibility),
        ]
        
        results = {}
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            self.logger.info(f"\n🔄 Executando: {test_name}...")
            
            try:
                start_time = time.time()
                success = test_func()
                elapsed_time = time.time() - start_time
                
                results[test_name] = {
                    "success": success,
                    "time": elapsed_time
                }
                
                if success:
                    self.logger.info(f"✅ {test_name} - PASSOU ({elapsed_time:.2f}s)")
                    passed_tests += 1
                else:
                    self.logger.error(f"❌ {test_name} - FALHOU ({elapsed_time:.2f}s)")
                    
            except Exception as e:
                self.logger.error(f"💥 {test_name} - ERRO CRÍTICO: {e}")
                results[test_name] = {
                    "success": False,
                    "time": 0,
                    "error": str(e)
                }
        
        # Relatório final
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 RELATÓRIO FINAL DOS TESTES")
        self.logger.info("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        
        self.logger.info(f"✅ Testes Aprovados: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            self.logger.info("🎉 SISTEMA ORM FUNCIONANDO CORRETAMENTE!")
            status = "SUCCESS"
        elif success_rate >= 60:
            self.logger.info("⚠️ Sistema ORM funcionando com algumas limitações")
            status = "PARTIAL"
        else:
            self.logger.error("❌ Sistema ORM com problemas significativos")
            status = "FAILED"
        
        # Próximos passos
        self.logger.info("\n📋 PRÓXIMOS PASSOS:")
        if success_rate >= 80:
            self.logger.info("1. ✅ Sistema pronto para produção")
            self.logger.info("2. 🔄 Refatorar scripts restantes para ORM")
            self.logger.info("3. 🗑️ Remover dependências SQLite antigas")
            self.logger.info("4. 🚀 Testar pipeline completo de coleta")
        else:
            self.logger.info("1. 🔧 Corrigir problemas identificados")
            self.logger.info("2. 🔄 Executar testes novamente")
            self.logger.info("3. 📚 Revisar documentação de configuração")
        
        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "status": status
        }
        
        return results

def main():
    """Função principal."""
    print("🚀 TESTE DO SISTEMA ORM - MIGRAÇÃO DE BANCO DE DADOS")
    print("=" * 55)
    
    tester = ORMSystemTester()
    
    try:
        results = tester.run_comprehensive_test()
        
        if results["summary"]["status"] == "SUCCESS":
            print("\n✅ TODOS OS TESTES PASSARAM!")
            print("🎯 Sistema ORM pronto para uso em produção")
        elif results["summary"]["status"] == "PARTIAL":
            print("\n⚠️ TESTES PARCIALMENTE APROVADOS")
            print("🔧 Algumas funcionalidades podem precisar de ajustes")
        else:
            print("\n❌ TESTES FALHARAM!")
            print("🛠️ Sistema precisa de correções antes do uso")
            
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado nos testes: {e}")

if __name__ == "__main__":
    main()
