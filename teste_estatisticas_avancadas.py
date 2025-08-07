#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE COLETA DE ESTATISTICAS AVANÇADAS - VERSÃO SIMPLIFICADA
==========================================================

Script simplificado para testar a coleta de estatísticas avançadas (xG, xA, formações táticas)
usando o AdvancedMatchScraper integrado ao ColetorEstatisticas.

Funcionalidades testadas:
1. Conexão com banco de dados
2. Coleta de estatísticas avançadas
3. Processamento de relatórios de partida
4. Atualização do banco de dados
"""

import logging
import sys
import os
import traceback
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,  # Nível DEBUG para mais detalhes
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('teste_estatisticas_avancadas.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class TesteEstatisticasAvancadas:
    """Classe para testar a coleta de estatísticas avançadas."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = {}
        
    def setup_database(self) -> bool:
        """Configura a conexão com o banco de dados de forma simplificada."""
        try:
            self.logger.info("🔍 Iniciando configuração do banco de dados...")
            
            # Importar apenas o necessário
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            
            # Configuração direta do banco de dados (substitua conforme necessário)
            db_url = os.getenv('DATABASE_URL', 'postgresql://apostapro_user:apostapro_pass@localhost:5432/apostapro_db')
            self.logger.info(f"Conectando ao banco de dados: {db_url}")
            
            # Criar engine com configurações básicas
            self.engine = create_engine(db_url, pool_pre_ping=True)
            
            # Testar conexão
            try:
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    self.logger.info("✅ Conexão com o banco de dados bem-sucedida")
            except Exception as e:
                self.logger.error(f"❌ Falha na conexão com o banco de dados: {e}")
                return False
            
            # Configurar a sessão
            self.Session = sessionmaker(bind=self.engine)
            self.logger.info("✅ Sessão do banco de dados configurada com sucesso")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar banco de dados: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def obter_partidas_teste(self, limite: int = 2) -> List[Dict]:
        """Obtém partidas para teste."""
        try:
            session = self.Session()
            
            # Buscar partidas com status 'pendente' e URLs válidas
            result = session.execute(
                """
                SELECT id, url_match_report 
                FROM partidas 
                WHERE (status_coleta_detalhada = 'pendente' OR status_coleta_detalhada IS NULL)
                AND url_match_report IS NOT NULL
                AND url_match_report != ''
                ORDER BY id
                LIMIT :limite
                """,
                {'limite': limite}
            )
            
            partidas = [{'id': row[0], 'url': row[1]} for row in result]
            session.close()
            
            if not partidas:
                self.logger.warning("Nenhuma partida pendente encontrada para teste")
                return []
                
            self.logger.info(f"Encontradas {len(partidas)} partidas para teste")
            return partidas
            
        except Exception as e:
            self.logger.error(f"Erro ao obter partidas para teste: {e}")
            if 'session' in locals():
                session.close()
            return []
    
    def testar_coleta_avancada(self, partida_id: int, match_url: str) -> bool:
        """Testa a coleta de estatísticas avançadas para uma partida."""
        from bs4 import BeautifulSoup
        from Coleta_de_dados.apis.fbref.coletar_estatisticas_detalhadas import ColetorEstatisticas
        from Coleta_de_dados.apis.fbref.fbref_utils import fazer_requisicao
        
        self.logger.info(f"\n🔍 Testando coleta avançada para partida {partida_id}")
        self.logger.info(f"URL: {match_url}")
        
        try:
            # Fazer requisição da página
            soup = fazer_requisicao(match_url)
            if not soup:
                self.logger.error("Falha ao obter a página da partida")
                return False
            
            # Inicializar coletor
            coletor = ColetorEstatisticas(session=self.Session())
            
            # Processar relatório da partida
            sucesso, num_jogadores = coletor.processar_match_report(
                soup=soup,
                partida_id=partida_id,
                match_url=match_url
            )
            
            if not sucesso or num_jogadores == 0:
                self.logger.error("Falha ao processar estatísticas da partida")
                return False
            
            # Verificar se as estatísticas avançadas foram salvas
            session = self.Session()
            estatisticas = session.execute(
                """
                SELECT xg_casa, xg_visitante, formacao_casa, formacao_visitante
                FROM estatisticas_partidas
                WHERE partida_id = :partida_id
                """,
                {'partida_id': partida_id}
            ).fetchone()
            
            if not estatisticas:
                self.logger.error("Estatísticas avançadas não encontradas no banco de dados")
                return False
            
            xg_casa, xg_visitante, formacao_casa, formacao_visitante = estatisticas
            
            self.logger.info("\n📊 Estatísticas avançadas coletadas:")
            self.logger.info(f"- xG Casa: {xg_casa}")
            self.logger.info(f"- xG Visitante: {xg_visitante}")
            self.logger.info(f"- Formação Casa: {formacao_casa}")
            self.logger.info(f"- Formação Visitante: {formacao_visitante}")
            
            # Verificar se os valores são válidos
            if xg_casa is None or xg_visitante is None:
                self.logger.warning("Valores de xG ausentes")
            if not formacao_casa or not formacao_visitante:
                self.logger.warning("Formações táticas ausentes")
            
            session.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Erro durante o teste de coleta avançada: {e}", exc_info=True)
            if 'session' in locals():
                session.close()
            return False
    
    def executar_testes(self):
        """Executa todos os testes."""
        self.logger.info("🚀 Iniciando teste de coleta de estatísticas avançadas")
        
        # Configurar banco de dados
        if not self.setup_database():
            self.logger.error("❌ Teste abortado: falha na configuração do banco de dados")
            return False
        
        # Obter partidas para teste
        partidas = self.obter_partidas_teste(limite=2)
        if not partidas:
            self.logger.error("❌ Nenhuma partida disponível para teste")
            return False
        
        # Executar testes
        resultados = []
        for partida in partidas:
            sucesso = self.testar_coleta_avancada(partida['id'], partida['url'])
            resultados.append((partida['id'], sucesso))
        
        # Resumo dos resultados
        total = len(resultados)
        sucessos = sum(1 for _, s in resultados if s)
        
        self.logger.info("\n" + "="*50)
        self.logger.info("📋 RESUMO DOS TESTES")
        self.logger.info("="*50)
        
        for partida_id, sucesso in resultados:
            status = "✅ SUCESSO" if sucesso else "❌ FALHA"
            self.logger.info(f"Partida {partida_id}: {status}")
        
        self.logger.info("-"*50)
        self.logger.info(f"Total de testes: {total}")
        self.logger.info(f"Sucessos: {sucessos}")
        self.logger.info(f"Falhas: {total - sucessos}")
        
        if sucessos == total:
            self.logger.info("\n🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
        else:
            self.logger.warning(f"\n⚠️ {total - sucessos} TESTES FALHARAM")
        
        return sucessos == total

def main():
    """Função principal."""
    tester = TesteEstatisticasAvancadas()
    return 0 if tester.executar_testes() else 1

if __name__ == "__main__":
    sys.exit(main())
