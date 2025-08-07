"""
Módulo otimizado para coleta de dados de partidas do FBRef.
Versão melhorada com melhor tratamento de erros, performance e manutenibilidade.
"""

import logging
import sqlite3
import os
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from contextlib import contextmanager
from tqdm import tqdm

from .fbref_utils import fazer_requisicao, BASE_URL, driver_context

# Configurações com caminho absoluto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')

logger = logging.getLogger(__name__)

@dataclass
class PartidaInfo:
    """Classe para estruturar informações de uma partida."""
    data: str
    time_casa: str
    placar: str
    time_visitante: str
    url_match_report: str

class ColetorPartidas:
    """Classe principal para coleta de dados de partidas."""
    
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self.stats = {
            'links_processados': 0,
            'links_com_erro': 0,
            'partidas_encontradas': 0,
            'links_sem_partidas': 0
        }

    @contextmanager
    def get_db_connection(self):
        """Context manager para conexões com o banco de dados."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA journal_mode=WAL')  # Melhora performance
            conn.execute('PRAGMA synchronous=NORMAL')
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Erro no banco de dados: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def encontrar_link_scores_and_fixtures(self, url_temporada: str) -> Optional[str]:
        """
        Navega até a página principal de uma temporada e encontra o link para a 
        página 'Scores & Fixtures' usando múltiplas estratégias.

        Args:
            url_temporada (str): A URL da página principal (Stats) de uma temporada.

        Returns:
            str or None: A URL completa para a página 'Scores & Fixtures' ou None se não for encontrada.
        """
        logger.info(f"  -> Buscando link de 'Scores & Fixtures' em: {url_temporada}")
        
        soup = fazer_requisicao(url_temporada)
        if not soup:
            logger.error("   -> Falha ao obter o conteúdo da página da temporada.")
            return None

        # Estratégia 1: Procurar no menu de navegação interno (mais confiável)
        inner_nav = soup.find('div', id='inner_nav')
        if inner_nav:
            link_tag = inner_nav.find('a', href=lambda href: href and '/schedule/' in href)
            if link_tag and link_tag.get('href'):
                link_completo = f"{BASE_URL}{link_tag['href']}"
                logger.info(f"   -> Link encontrado pelo inner_nav: {link_completo}")
                return link_completo

        # Estratégia 2: Procurar no menu de navegação da seção
        nav_menu = soup.find('div', class_='section_menu')
        if nav_menu:
            link_tag = nav_menu.find('a', string='Scores & Fixtures')
            if link_tag and link_tag.get('href'):
                link_completo = f"{BASE_URL}{link_tag['href']}"
                logger.info(f"   -> Link encontrado pelo section_menu: {link_completo}")
                return link_completo
                
        # Estratégia 3: Buscar por seletor CSS específico
        link_css = soup.select_one('a[href*="/schedule/"]')
        if link_css and link_css.get('href'):
            link_completo = f"{BASE_URL}{link_css['href']}"
            logger.info(f"   -> Link encontrado por CSS selector: {link_completo}")
            return link_completo

        # Estratégia 4 (Fallback): Procurar em toda a página
        all_links = soup.find_all('a', string='Scores & Fixtures')
        for link_tag in all_links:
            href = link_tag.get('href', '')
            if href and 'schedule' in href:
                link_completo = f"{BASE_URL}{href}"
                logger.info(f"   -> Link (fallback) encontrado: {link_completo}")
                return link_completo

        logger.warning(f"   -> AVISO: Não foi possível encontrar o link para 'Scores & Fixtures'.")
        return None

    def extrair_partida_da_linha(self, linha, base_url: str = BASE_URL) -> Optional[PartidaInfo]:
        """
        Extrai informações de uma partida a partir de uma linha da tabela.
        
        Args:
            linha: Elemento tr da tabela de partidas
            base_url: URL base para construir links completos
            
        Returns:
            PartidaInfo or None: Informações da partida ou None se inválida
        """
        try:
            # Pula linhas de cabeçalho
            if 'thead' in linha.get('class', []):
                return None
                
            cols = linha.find_all('td')
            if len(cols) < 5:  # Verifica se há colunas suficientes
                return None
                
            # Extrai informações básicas - estrutura corrigida baseada no HTML real
            data = cols[0].get_text(strip=True) if len(cols) > 0 else ""
            time_casa = cols[2].get_text(strip=True) if len(cols) > 2 else ""
            placar = cols[4].get_text(strip=True) if len(cols) > 4 else ""
            time_visitante = cols[6].get_text(strip=True) if len(cols) > 6 else ""
            
            # Verifica se há placar (indica que o jogo aconteceu)
            if not placar or placar in ['', '-', 'vs', 'TBD']:
                return None
                
            # Busca o link do match report - CORREÇÃO: agora procura na coluna de score
            url_match_report = None
            
            # Estratégia 1: Procurar na coluna de score (onde está o link da partida)
            score_cell = cols[4] if len(cols) > 4 else None
            if score_cell:
                score_link = score_cell.find('a')
                if score_link and score_link.get('href'):
                    url_match_report = f"{base_url}{score_link['href']}"
                    logger.debug(f"Link encontrado na coluna score: {url_match_report}")
            
            # Estratégia 2: Procurar em toda a linha por links de partida
            if not url_match_report:
                for col in cols:
                    link_tag = col.find('a')
                    if link_tag and link_tag.get('href') and '/matches/' in link_tag['href']:
                        url_match_report = f"{base_url}{link_tag['href']}"
                        logger.debug(f"Link encontrado em coluna genérica: {url_match_report}")
                        break
            
            # Estratégia 3: Procurar por "Match Report" específico
            if not url_match_report:
                for col in cols:
                    link_tag = col.find('a', string='Match Report')
                    if link_tag and link_tag.get('href'):
                        url_match_report = f"{base_url}{link_tag['href']}"
                        logger.debug(f"Link Match Report encontrado: {url_match_report}")
                        break
            
            if not url_match_report:
                logger.debug(f"Nenhum link de partida encontrado para: {time_casa} vs {time_visitante}")
                return None
            
            return PartidaInfo(
                data=data,
                time_casa=time_casa,
                placar=placar,
                time_visitante=time_visitante,
                url_match_report=url_match_report
            )
            
        except (IndexError, AttributeError) as e:
            logger.debug(f"Erro ao processar linha da tabela: {e}")
            return None

    def extrair_links_de_partidas(self, url_scores_fixtures: str) -> List[PartidaInfo]:
        """
        A partir da página 'Scores & Fixtures', extrai todas as informações de partidas.

        Args:
            url_scores_fixtures (str): A URL da página com a lista de jogos.

        Returns:
            List[PartidaInfo]: Lista de informações das partidas.
        """
        logger.info(f"   -> Extraindo dados de partidas de: {url_scores_fixtures}")
        
        soup = fazer_requisicao(url_scores_fixtures)
        if not soup:
            logger.error("   -> Falha ao obter o conteúdo da página de Scores & Fixtures.")
            return []

        partidas = []
        
        # Busca tabelas de jogos (múltiplas estratégias)
        tabelas_candidatas = (
            soup.select("table[id*='sched_']") or  # Estratégia 1: ID específico
            soup.select("table.stats_table") or   # Estratégia 2: Classe específica
            soup.find_all('table')                 # Estratégia 3: Todas as tabelas
        )

        if not tabelas_candidatas:
            logger.warning("   -> Nenhuma tabela encontrada na página.")
            return []

        # Processa cada tabela candidata
        for tabela in tabelas_candidatas:
            tbody = tabela.find('tbody')
            if not tbody:
                continue
                
            # Verifica se é uma tabela de jogos válida
            caption = tabela.find('caption')
            if caption and any(keyword in caption.get_text().lower() 
                             for keyword in ['scores', 'fixtures', 'matches', 'results']):
                logger.debug("   -> Tabela de jogos identificada pelo caption.")
            
            # Processa cada linha da tabela
            for linha in tbody.find_all('tr'):
                partida = self.extrair_partida_da_linha(linha)
                if partida:
                    partidas.append(partida)

        # Remove duplicatas baseado na URL do match report
        partidas_unicas = []
        urls_vistas = set()
        
        for partida in partidas:
            if partida.url_match_report not in urls_vistas:
                partidas_unicas.append(partida)
                urls_vistas.add(partida.url_match_report)

        if not partidas_unicas:
            logger.warning("   -> AVISO: Nenhuma partida com 'Match Report' foi encontrada.")
        else:
            logger.info(f"   -> Encontradas {len(partidas_unicas)} partidas únicas com 'Match Report'.")
            
        return partidas_unicas

    def salvar_partidas_no_banco(self, partidas: List[PartidaInfo], link_coleta_id: int) -> int:
        """
        Salva as partidas no banco de dados.
        
        Args:
            partidas: Lista de informações das partidas
            link_coleta_id: ID do link de coleta relacionado
            
        Returns:
            int: Número de partidas salvas
        """
        if not partidas:
            return 0
            
        partidas_salvas = 0
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            for partida in partidas:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO partidas 
                        (link_coleta_id, data, time_casa, placar, time_visitante, url_match_report, status_coleta_detalhada) 
                        VALUES (?, ?, ?, ?, ?, ?, 'pendente')
                    """, (
                        link_coleta_id,
                        partida.data,
                        partida.time_casa,
                        partida.placar,
                        partida.time_visitante,
                        partida.url_match_report
                    ))
                    
                    if cursor.rowcount > 0:
                        partidas_salvas += 1
                        
                except sqlite3.Error as e:
                    logger.error(f"Erro ao salvar partida no banco: {e}")
                    continue
            
            conn.commit()
            
        logger.info(f"  -> {partidas_salvas} partidas salvas no banco de dados.")
        return partidas_salvas

    def processar_link_temporada(self, link_id: int, url_temporada: str) -> Tuple[bool, str]:
        """
        Processa um link de temporada individual.
        
        Args:
            link_id: ID do link no banco
            url_temporada: URL da temporada a processar
            
        Returns:
            Tuple[bool, str]: (sucesso, status_final)
        """
        logger.info(f"\n--- Processando link ID {link_id}: {url_temporada} ---")
        
        try:
            # Etapa 1: Encontrar a página de jogos ('Scores & Fixtures')
            url_jogos = self.encontrar_link_scores_and_fixtures(url_temporada)
            
            if not url_jogos:
                logger.error(f"   -> Falha ao encontrar a página de jogos para o link ID {link_id}.")
                return False, 'erro'
                
            # Etapa 2: Extrair os dados das partidas da página de jogos
            partidas = self.extrair_links_de_partidas(url_jogos)
            
            if not partidas:
                logger.warning(f"   -> Nenhuma partida encontrada para o link ID {link_id}.")
                return False, 'sem_partidas'
                
            # Etapa 3: Salvar partidas no banco
            partidas_salvas = self.salvar_partidas_no_banco(partidas, link_id)
            
            if partidas_salvas > 0:
                self.stats['partidas_encontradas'] += partidas_salvas
                return True, 'concluido'
            else:
                return False, 'erro_salvamento'
                
        except Exception as e:
            logger.error(f"Erro inesperado ao processar link ID {link_id}: {e}", exc_info=True)
            return False, 'erro'

    def atualizar_status_link(self, link_id: int, status: str) -> None:
        """Atualiza o status de um link no banco de dados."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE links_para_coleta SET status_coleta = ? WHERE id = ?", 
                    (status, link_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Erro ao atualizar status do link {link_id}: {e}")

    def obter_links_pendentes(self) -> List[Tuple[int, str]]:
        """Obtém links pendentes de processamento do banco de dados."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, url 
                    FROM links_para_coleta 
                    WHERE status_coleta IN ('pendente', 'erro') OR status_coleta IS NULL
                    ORDER BY id
                """)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter links pendentes: {e}")
            return []

    def executar_coleta(self) -> Dict[str, int]:
        """
        Executa o processo completo de coleta de dados de partidas.
        
        Returns:
            Dict[str, int]: Estatísticas da execução
        """
        logger.info("🚀 Iniciando Script 2: Coleta de Dados de Partidas...")
        
        # Obter links para processar
        links_para_processar = self.obter_links_pendentes()
        
        if not links_para_processar:
            logger.info("Nenhum link novo para processar. Script 2 finalizado.")
            return self.stats

        logger.info(f"Encontrados {len(links_para_processar)} links pendentes para processar.")
        
        # Processar cada link com barra de progresso
        for link_id, url_temporada in tqdm(links_para_processar, desc="Coletando Links de Partidas"):
            sucesso, status = self.processar_link_temporada(link_id, url_temporada)
            
            # Atualizar estatísticas
            if sucesso:
                self.stats['links_processados'] += 1
            else:
                if status == 'sem_partidas':
                    self.stats['links_sem_partidas'] += 1
                else:
                    self.stats['links_com_erro'] += 1
            
            # Atualizar status no banco
            self.atualizar_status_link(link_id, status)
        
        # Log final com estatísticas
        logger.info("\n=== ESTATÍSTICAS FINAIS ===")
        logger.info(f"Links processados com sucesso: {self.stats['links_processados']}")
        logger.info(f"Links sem partidas: {self.stats['links_sem_partidas']}")
        logger.info(f"Links com erro: {self.stats['links_com_erro']}")
        logger.info(f"Total de partidas encontradas: {self.stats['partidas_encontradas']}")
        logger.info("✅ Script 2 (Coleta de Partidas) finalizado com sucesso!")
        
        return self.stats


def main():
    """Função principal para execução standalone do módulo."""
    try:
        # Garantir que o diretório do banco existe
        os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
        
        # Executar coleta
        coletor = ColetorPartidas()
        stats = coletor.executar_coleta()
        
        return stats
        
    except Exception as e:
        logger.critical(f"Erro crítico na execução principal: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    main()