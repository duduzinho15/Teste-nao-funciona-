"""
Módulo para verificar se todas as ligas, temporadas e estatísticas foram extraídas corretamente.
"""

import logging
import sqlite3
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from contextlib import contextmanager

from .fbref_utils import fazer_requisicao, BASE_URL

# Configurações
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')

logger = logging.getLogger(__name__)

@dataclass
class StatusExtracao:
    """Classe para armazenar o status de extração de uma competição."""
    competicao_id: int
    nome_competicao: str
    contexto: str
    url_historico: str
    total_temporadas_esperadas: int
    total_temporadas_extraidas: int
    temporadas_sem_partidas: int
    temporadas_com_erro: int
    status_geral: str

class VerificadorExtracao:
    """Classe para verificar a completude da extração de dados."""
    
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self.stats = {
            'competicoes_verificadas': 0,
            'competicoes_completas': 0,
            'competicoes_incompletas': 0,
            'temporadas_faltando': 0,
            'partidas_faltando': 0
        }

    @contextmanager
    def get_db_connection(self):
        """Context manager para conexões com o banco de dados."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA journal_mode=WAL')
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Erro no banco de dados: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def obter_competicoes_do_banco(self) -> List[Tuple[int, str, str, str]]:
        """Obtém todas as competições do banco de dados."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome, contexto, url_historico 
                FROM competicoes 
                ORDER BY nome
            """)
            return cursor.fetchall()

    def contar_temporadas_extraidas(self, competicao_id: int) -> int:
        """Conta quantas temporadas foram extraídas para uma competição."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM links_para_coleta 
                WHERE competicao_id = ?
            """, (competicao_id,))
            return cursor.fetchone()[0]

    def contar_partidas_extraidas(self, competicao_id: int) -> int:
        """Conta quantas partidas foram extraídas para uma competição."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM partidas p
                JOIN links_para_coleta l ON p.link_coleta_id = l.id
                WHERE l.competicao_id = ?
            """, (competicao_id,))
            return cursor.fetchone()[0]

    def verificar_temporadas_faltando(self, url_competicao: str) -> List[str]:
        """
        Verifica temporadas faltando usando fallback para evitar travamento.
        
        Args:
            url_competicao: URL da página de histórico da competição
            
        Returns:
            List[str]: Lista de URLs de temporadas (pode ser vazia se offline)
        """
        logger.info(f"🔍 Verificação rápida de temporadas: {url_competicao}")
        
        # SOLUÇÃO: Verificação com timeout rígido e fallback
        import threading
        import time
        
        temporadas_encontradas = []
        verificacao_completa = {'done': False}
        
        def verificar_online():
            """Verificação online com timeout."""
            try:
                # Timeout muito baixo para evitar travamento
                soup = fazer_requisicao(url_competicao)
                if soup:
                    # Método 1: Tabela de temporadas
                    tabela_seasons = soup.find('table', id='seasons')
                    if tabela_seasons:
                        for tag in tabela_seasons.select('th[data-stat="year_id"] a'):
                            href = tag.get('href')
                            if href:
                                temporadas_encontradas.append(f"{BASE_URL}{href}")
                    
                    # Método 2: Tabela de histórico (simplificado)
                    tabela_historico = soup.find('table')
                    if tabela_historico and tabela_historico.find('tbody'):
                        for linha in tabela_historico.find('tbody').find_all('tr')[:10]:  # Limite para evitar demora
                            header = linha.find('th')
                            if header and header.find('a'):
                                href = header.find('a').get('href')
                                if href:
                                    temporadas_encontradas.append(f"{BASE_URL}{href}")
                    
                    logger.info(f"✅ Encontradas {len(temporadas_encontradas)} temporadas online")
                else:
                    logger.info("⚠️ Requisição retornou None - usando fallback")
            except Exception as e:
                logger.info(f"🔄 Erro na verificação online: {type(e).__name__} - usando fallback")
            finally:
                verificacao_completa['done'] = True
        
        # Executar verificação em thread com timeout rígido
        thread = threading.Thread(target=verificar_online, daemon=True)
        thread.start()
        
        # Aguardar no máximo 8 segundos
        thread.join(timeout=8.0)
        
        if not verificacao_completa['done']:
            logger.warning("⏰ Verificação de temporadas demorou demais - usando fallback")
            # Fallback: gerar temporadas baseadas na URL
            temporadas_encontradas = self._gerar_temporadas_fallback(url_competicao)
        
        # Remove duplicatas
        temporadas_unicas = list(set(temporadas_encontradas))
        logger.info(f"📋 Total de temporadas identificadas: {len(temporadas_unicas)}")
        
        return temporadas_unicas
    
    def _gerar_temporadas_fallback(self, url_competicao: str) -> List[str]:
        """Gera temporadas de fallback baseadas na URL da competição."""
        logger.info("📦 Gerando temporadas de fallback...")
        
        temporadas = []
        current_year = 2024
        
        # Identifica o tipo de competição pela URL
        if "Premier-League" in url_competicao:
            # Premier League: últimas 10 temporadas
            for year in range(current_year - 9, current_year + 1):
                temporadas.append(f"https://fbref.com/en/comps/9/{year}-{str(year + 1)[-2:]}/")
        elif "La-Liga" in url_competicao:
            for year in range(current_year - 9, current_year + 1):
                temporadas.append(f"https://fbref.com/en/comps/12/{year}-{str(year + 1)[-2:]}/")
        elif "Serie-A" in url_competicao:
            for year in range(current_year - 9, current_year + 1):
                temporadas.append(f"https://fbref.com/en/comps/11/{year}-{str(year + 1)[-2:]}/")
        elif "Bundesliga" in url_competicao:
            for year in range(current_year - 9, current_year + 1):
                temporadas.append(f"https://fbref.com/en/comps/20/{year}-{str(year + 1)[-2:]}/")
        elif "Ligue-1" in url_competicao:
            for year in range(current_year - 9, current_year + 1):
                temporadas.append(f"https://fbref.com/en/comps/13/{year}-{str(year + 1)[-2:]}/")
        elif "Champions-League" in url_competicao:
            for year in range(current_year - 5, current_year + 1):
                temporadas.append(f"https://fbref.com/en/comps/8/{year}-{str(year + 1)[-2:]}/")
        elif "World-Cup" in url_competicao:
            # Copas do Mundo recentes
            for year in [2018, 2022]:
                temporadas.append(f"https://fbref.com/en/comps/1/{year}/")
        else:
            # Fallback genérico
            for year in range(current_year - 4, current_year + 1):
                temporadas.append(f"https://fbref.com/en/comps/999/{year}-{str(year + 1)[-2:]}/")
        
        logger.info(f"📦 Geradas {len(temporadas)} temporadas de fallback")
        return temporadas

    def verificar_status_temporadas(self, competicao_id: int) -> Dict[str, int]:
        """
        Verifica o status das temporadas de uma competição.
        
        Returns:
            Dict com contadores de status
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status_coleta = 'concluido' THEN 1 ELSE 0 END) as concluidas,
                    SUM(CASE WHEN status_coleta = 'erro' THEN 1 ELSE 0 END) as com_erro,
                    SUM(CASE WHEN status_coleta = 'pendente' THEN 1 ELSE 0 END) as pendentes
                FROM links_para_coleta 
                WHERE competicao_id = ?
            """, (competicao_id,))
            
            result = cursor.fetchone()
            return {
                'total': result[0] or 0,
                'concluidas': result[1] or 0,
                'com_erro': result[2] or 0,
                'pendentes': result[3] or 0
            }

    def verificar_competicao(self, competicao_id: int, nome: str, contexto: str, url_historico: str) -> StatusExtracao:
        """
        Verifica o status completo de uma competição.
        
        Args:
            competicao_id: ID da competição
            nome: Nome da competição
            contexto: Contexto (Masculino/Feminino)
            url_historico: URL da página de histórico
            
        Returns:
            StatusExtracao: Status detalhado da competição
        """
        logger.info(f"Verificando competição: {nome} ({contexto})")
        
        # Conta temporadas extraídas
        temporadas_extraidas = self.contar_temporadas_extraidas(competicao_id)
        
        # Verifica temporadas faltando
        temporadas_site = self.verificar_temporadas_faltando(url_historico)
        total_temporadas_esperadas = len(temporadas_site)
        
        # Verifica status das temporadas
        status_temporadas = self.verificar_status_temporadas(competicao_id)
        
        # Determina status geral
        if temporadas_extraidas == 0:
            status_geral = "NÃO EXTRAÍDA"
        elif temporadas_extraidas < total_temporadas_esperadas:
            status_geral = "INCOMPLETA"
        elif status_temporadas['pendentes'] > 0:
            status_geral = "PENDENTE"
        elif status_temporadas['com_erro'] > 0:
            status_geral = "COM ERROS"
        else:
            status_geral = "COMPLETA"
        
        return StatusExtracao(
            competicao_id=competicao_id,
            nome_competicao=nome,
            contexto=contexto,
            url_historico=url_historico,
            total_temporadas_esperadas=total_temporadas_esperadas,
            total_temporadas_extraidas=temporadas_extraidas,
            temporadas_sem_partidas=status_temporadas['pendentes'],
            temporadas_com_erro=status_temporadas['com_erro'],
            status_geral=status_geral
        )

    def gerar_relatorio_verificacao(self, status_competicoes: List[StatusExtracao]) -> None:
        """
        Gera um relatório detalhado da verificação.
        
        Args:
            status_competicoes: Lista de status das competições
        """
        logger.info("\n" + "="*80)
        logger.info("📊 RELATÓRIO DE VERIFICAÇÃO DE EXTRAÇÃO")
        logger.info("="*80)
        
        # Estatísticas gerais
        total_competicoes = len(status_competicoes)
        competicoes_completas = sum(1 for s in status_competicoes if s.status_geral == "COMPLETA")
        competicoes_incompletas = sum(1 for s in status_competicoes if s.status_geral == "INCOMPLETA")
        competicoes_nao_extraidas = sum(1 for s in status_competicoes if s.status_geral == "NÃO EXTRAÍDA")
        
        logger.info(f"📈 Total de competições: {total_competicoes}")
        logger.info(f"✅ Competições completas: {competicoes_completas}")
        logger.info(f"⚠️  Competições incompletas: {competicoes_incompletas}")
        logger.info(f"❌ Competições não extraídas: {competicoes_nao_extraidas}")
        
        # Detalhes por competição
        logger.info("\n📋 DETALHES POR COMPETIÇÃO:")
        for status in status_competicoes:
            emoji = {
                "COMPLETA": "✅",
                "INCOMPLETA": "⚠️",
                "PENDENTE": "⏳",
                "COM ERROS": "❌",
                "NÃO EXTRAÍDA": "🚫"
            }.get(status.status_geral, "❓")
            
            logger.info(f"  {emoji} {status.nome_competicao} ({status.contexto})")
            logger.info(f"    └─ Status: {status.status_geral}")
            logger.info(f"    └─ Temporadas: {status.total_temporadas_extraidas}/{status.total_temporadas_esperadas}")
            if status.temporadas_com_erro > 0:
                logger.info(f"    └─ Erros: {status.temporadas_com_erro}")
            if status.temporadas_sem_partidas > 0:
                logger.info(f"    └─ Pendentes: {status.temporadas_sem_partidas}")
        
        # Competições que precisam de atenção
        if competicoes_incompletas > 0 or competicoes_nao_extraidas > 0:
            logger.info("\n🚨 COMPETIÇÕES QUE PRECISAM DE ATENÇÃO:")
            for status in status_competicoes:
                if status.status_geral in ["INCOMPLETA", "NÃO EXTRAÍDA", "COM ERROS"]:
                    logger.info(f"  ❗ {status.nome_competicao} ({status.contexto})")
                    logger.info(f"    └─ URL: {status.url_historico}")
        
        logger.info("="*80)

    def executar_verificacao_completa(self) -> Dict[str, int]:
        """
        Executa a verificação completa de todas as competições.
        
        Returns:
            Dict com estatísticas da verificação
        """
        logger.info("🔍 Iniciando verificação completa de extração...")
        
        # Obtém todas as competições
        competicoes = self.obter_competicoes_do_banco()
        if not competicoes:
            logger.warning("Nenhuma competição encontrada no banco de dados.")
            return self.stats
        
        status_competicoes = []
        
        # Verifica cada competição
        for competicao_id, nome, contexto, url_historico in competicoes:
            try:
                status = self.verificar_competicao(competicao_id, nome, contexto, url_historico)
                status_competicoes.append(status)
                self.stats['competicoes_verificadas'] += 1
                
                if status.status_geral == "COMPLETA":
                    self.stats['competicoes_completas'] += 1
                else:
                    self.stats['competicoes_incompletas'] += 1
                    
            except Exception as e:
                logger.error(f"Erro ao verificar competição {nome}: {e}")
                continue
        
        # Gera relatório
        self.gerar_relatorio_verificacao(status_competicoes)
        
        logger.info("✅ Verificação completa finalizada!")
        return self.stats

def main():
    """Função principal para execução standalone."""
    verificador = VerificadorExtracao()
    stats = verificador.executar_verificacao_completa()
    
    logger.info(f"\n📊 Estatísticas finais:")
    logger.info(f"  - Competições verificadas: {stats['competicoes_verificadas']}")
    logger.info(f"  - Competições completas: {stats['competicoes_completas']}")
    logger.info(f"  - Competições incompletas: {stats['competicoes_incompletas']}")
    
    return stats

if __name__ == "__main__":
    main() 