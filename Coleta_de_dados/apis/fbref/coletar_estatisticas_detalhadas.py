"""
Módulo otimizado para coleta de estatísticas detalhadas de partidas do FBRef.
Versão melhorada com melhor tratamento de erros, performance e estruturação de dados.
"""

import logging
import sqlite3
import os
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from contextlib import contextmanager
from tqdm import tqdm
import json

from .fbref_utils import fazer_requisicao, limpar_recursos
from .scraper_estatisticas_avancadas import AdvancedMatchScraper

# Configurações com caminho absoluto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')

logger = logging.getLogger(__name__)

@dataclass
class EstatisticasJogador:
    """Classe para estruturar estatísticas completas de um jogador."""
    # Informações básicas
    partida_id: int
    jogador_nome: str
    time_nome: str
    nacao: str = ""
    posicao: str = ""
    idade: str = ""
    minutos_jogados: int = 0
    
    # Estatísticas padrão
    gols: int = 0
    assistencias: int = 0
    gols_penalti: int = 0
    penaltis_cobrados: int = 0
    cartoes_amarelos: int = 0
    cartoes_vermelhos: int = 0
    xg_jogador: float = 0.0
    npxg_jogador: float = 0.0
    xg_assist_jogador: float = 0.0
    xg_npxg_assist_jogador: float = 0.0
    
    # Ações de criação
    sca: int = 0
    gca: int = 0
    
    # Estatísticas de passe
    passes_completos: int = 0
    passes_tentados: int = 0
    passes_pct: float = 0.0
    passes_distancia_total: int = 0
    passes_distancia_progressiva: int = 0
    passes_curtos_completos: int = 0
    passes_curtos_tentados: int = 0
    passes_medios_completos: int = 0
    passes_medios_tentados: int = 0
    passes_longos_completos: int = 0
    passes_longos_tentados: int = 0
    passes_chave: int = 0
    passes_terco_final: int = 0
    passes_area_penal: int = 0
    cruzamentos_area_penal: int = 0
    
    # Estatísticas de defesa
    desarmes: int = 0
    desarmes_vencidos: int = 0
    bloqueios: int = 0
    chutes_bloqueados: int = 0
    passes_bloqueados: int = 0
    interceptacoes: int = 0
    erros_defensivos: int = 0
    disputas_vencidas_pct: float = 0.0
    
    # Estatísticas de posse
    toques: int = 0
    toques_terco_defensivo: int = 0
    toques_terco_medio: int = 0
    toques_terco_ofensivo: int = 0
    toques_area_defensiva: int = 0
    toques_area_ofensiva: int = 0
    dribles_tentados: int = 0
    dribles_completos: int = 0
    dribles_sucesso_pct: float = 0.0
    conducoes_progressivas: int = 0
    recepcoes_progressivas: int = 0
    
    # Estatísticas diversas
    faltas_cometidas: int = 0
    faltas_sofridas: int = 0
    recuperacoes: int = 0
    duelos_aereos_vencidos: int = 0
    duelos_aereos_perdidos: int = 0
    duelos_aereos_vencidos_pct: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Converte a instância para dicionário."""
        return {field.name: getattr(self, field.name) for field in self.__dataclass_fields__.values()}

class ColetorEstatisticas:
    """Classe principal para coleta de estatísticas detalhadas."""
    
    def __init__(self, db_path: str = DB_NAME, session=None):
        self.db_path = db_path
        self.stats = {
            'partidas_processadas': 0,
            'partidas_com_erro': 0,
            'jogadores_processados': 0,
            'partidas_sem_stats': 0,
            'partidas_com_stats_avancados': 0
        }
        
        # Inicializa o scraper de estatísticas avançadas
        self.advanced_scraper = AdvancedMatchScraper(session) if session else None
        
        # Mapeamento de data-stat para campos da classe
        self.stat_mapping = self._create_stat_mapping()

    def _create_stat_mapping(self) -> Dict[str, Tuple[str, type]]:
        """Cria mapeamento entre data-stat HTML e campos da classe."""
        return {
            # Informações básicas
            'player': ('jogador_nome', str),
            'nationality': ('nacao', str),
            'position': ('posicao', str),
            'age': ('idade', str),
            'minutes': ('minutos_jogados', int),
            
            # Estatísticas padrão
            'goals': ('gols', int),
            'assists': ('assistencias', int),
            'pens_made': ('gols_penalti', int),
            'pens_att': ('penaltis_cobrados', int),
            'cards_yellow': ('cartoes_amarelos', int),
            'cards_red': ('cartoes_vermelhos', int),
            'xg': ('xg_jogador', float),
            'npxg': ('npxg_jogador', float),
            'xg_assist': ('xg_assist_jogador', float),
            'sca': ('sca', int),
            'gca': ('gca', int),
            
            # Passes
            'passes_completed': ('passes_completos', int),
            'passes': ('passes_tentados', int),
            'passes_pct': ('passes_pct', float),
            'passes_total_distance': ('passes_distancia_total', int),
            'passes_progressive_distance': ('passes_distancia_progressiva', int),
            'passes_completed_short': ('passes_curtos_completos', int),
            'passes_short': ('passes_curtos_tentados', int),
            'passes_completed_medium': ('passes_medios_completos', int),
            'passes_medium': ('passes_medios_tentados', int),
            'passes_completed_long': ('passes_longos_completos', int),
            'passes_long': ('passes_longos_tentados', int),
            'assisted_shots': ('passes_chave', int),
            'passes_into_final_third': ('passes_terco_final', int),
            'passes_into_penalty_area': ('passes_area_penal', int),
            'crosses_into_penalty_area': ('cruzamentos_area_penal', int),
            
            # Defesa
            'tackles': ('desarmes', int),
            'tackles_won': ('desarmes_vencidos', int),
            'blocks': ('bloqueios', int),
            'blocked_shots': ('chutes_bloqueados', int),
            'blocked_passes': ('passes_bloqueados', int),
            'interceptions': ('interceptacoes', int),
            'errors': ('erros_defensivos', int),
            'tackles_interceptions': ('disputas_vencidas_pct', float),
            
            # Posse
            'touches': ('toques', int),
            'touches_def_3rd': ('toques_terco_defensivo', int),
            'touches_mid_3rd': ('toques_terco_medio', int),
            'touches_att_3rd': ('toques_terco_ofensivo', int),
            'touches_def_pen_area': ('toques_area_defensiva', int),
            'touches_att_pen_area': ('toques_area_ofensiva', int),
            'dribbles': ('dribles_tentados', int),
            'dribbles_completed': ('dribles_completos', int),
            'dribbles_completed_pct': ('dribles_sucesso_pct', float),
            'progressive_carries': ('conducoes_progressivas', int),
            'progressive_passes_received': ('recepcoes_progressivas', int),
            
            # Diversos
            'fouls': ('faltas_cometidas', int),
            'fouled': ('faltas_sofridas', int),
            'recoveries': ('recuperacoes', int),
            'aerials_won': ('duelos_aereos_vencidos', int),
            'aerials_lost': ('duelos_aereos_perdidos', int),
            'aerials_won_pct': ('duelos_aereos_vencidos_pct', float)
        }

    @contextmanager
    def get_db_connection(self):
        """Context manager para conexões com o banco de dados."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA journal_mode=WAL')
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

    def setup_database_stats(self) -> None:
        """Cria/Altera as tabelas de estatísticas para incluir todas as colunas."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            logger.info("Configurando banco de dados com a estrutura completa de estatísticas...")

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estatisticas_jogador_partida (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    partida_id INTEGER NOT NULL,
                    jogador_nome TEXT NOT NULL,
                    time_nome TEXT NOT NULL,
                    nacao TEXT,
                    posicao TEXT,
                    idade TEXT,
                    minutos_jogados INTEGER DEFAULT 0,
                    
                    -- Padrão
                    gols INTEGER DEFAULT 0,
                    assistencias INTEGER DEFAULT 0,
                    gols_penalti INTEGER DEFAULT 0,
                    penaltis_cobrados INTEGER DEFAULT 0,
                    cartoes_amarelos INTEGER DEFAULT 0,
                    cartoes_vermelhos INTEGER DEFAULT 0,
                    xg_jogador REAL DEFAULT 0.0,
                    npxg_jogador REAL DEFAULT 0.0,
                    xg_assist_jogador REAL DEFAULT 0.0,
                    xg_npxg_assist_jogador REAL DEFAULT 0.0,

                    -- Ações de Criação
                    sca INTEGER DEFAULT 0,
                    gca INTEGER DEFAULT 0,

                    -- Passe
                    passes_completos INTEGER DEFAULT 0,
                    passes_tentados INTEGER DEFAULT 0,
                    passes_pct REAL DEFAULT 0.0,
                    passes_distancia_total INTEGER DEFAULT 0,
                    passes_distancia_progressiva INTEGER DEFAULT 0,
                    passes_curtos_completos INTEGER DEFAULT 0,
                    passes_curtos_tentados INTEGER DEFAULT 0,
                    passes_medios_completos INTEGER DEFAULT 0,
                    passes_medios_tentados INTEGER DEFAULT 0,
                    passes_longos_completos INTEGER DEFAULT 0,
                    passes_longos_tentados INTEGER DEFAULT 0,
                    passes_chave INTEGER DEFAULT 0,
                    passes_terco_final INTEGER DEFAULT 0,
                    passes_area_penal INTEGER DEFAULT 0,
                    cruzamentos_area_penal INTEGER DEFAULT 0,
                    
                    -- Defesa
                    desarmes INTEGER DEFAULT 0,
                    desarmes_vencidos INTEGER DEFAULT 0,
                    bloqueios INTEGER DEFAULT 0,
                    chutes_bloqueados INTEGER DEFAULT 0,
                    passes_bloqueados INTEGER DEFAULT 0,
                    interceptacoes INTEGER DEFAULT 0,
                    erros_defensivos INTEGER DEFAULT 0,
                    disputas_vencidas_pct REAL DEFAULT 0.0,

                    -- Posse
                    toques INTEGER DEFAULT 0,
                    toques_terco_defensivo INTEGER DEFAULT 0,
                    toques_terco_medio INTEGER DEFAULT 0,
                    toques_terco_ofensivo INTEGER DEFAULT 0,
                    toques_area_defensiva INTEGER DEFAULT 0,
                    toques_area_ofensiva INTEGER DEFAULT 0,
                    dribles_tentados INTEGER DEFAULT 0,
                    dribles_completos INTEGER DEFAULT 0,
                    dribles_sucesso_pct REAL DEFAULT 0.0,
                    conducoes_progressivas INTEGER DEFAULT 0,
                    recepcoes_progressivas INTEGER DEFAULT 0,

                    -- Diversos
                    faltas_cometidas INTEGER DEFAULT 0,
                    faltas_sofridas INTEGER DEFAULT 0,
                    recuperacoes INTEGER DEFAULT 0,
                    duelos_aereos_vencidos INTEGER DEFAULT 0,
                    duelos_aereos_perdidos INTEGER DEFAULT 0,
                    duelos_aereos_vencidos_pct REAL DEFAULT 0.0,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    UNIQUE(partida_id, jogador_nome),
                    FOREIGN KEY (partida_id) REFERENCES partidas (id)
                )
            ''')
            
            # Criar índices para melhor performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_partida_jogador ON estatisticas_jogador_partida(partida_id, jogador_nome)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_time_nome ON estatisticas_jogador_partida(time_nome)')
            
            conn.commit()
            logger.info("Estrutura do banco de dados atualizada com sucesso.")

    def extrair_stat_seguro(self, linha, stat_name: str, tipo: type = float) -> Any:
        """
        Função auxiliar para extrair e converter uma estatística de forma segura.
        
        Args:
            linha: Elemento HTML da linha
            stat_name: Nome do atributo data-stat
            tipo: Tipo para conversão (int, float, str)
            
        Returns:
            Valor convertido ou valor padrão em caso de erro
        """
        try:
            tag = linha.find(['th', 'td'], {'data-stat': stat_name})
            if not tag:
                return tipo(0) if tipo in (int, float) else ""
                
            # O valor numérico costuma estar no atributo 'csk' para ordenação
            valor_str = tag.get('csk') or tag.get_text(strip=True)
            
            if not valor_str or valor_str in ['', '-', 'N/A']:
                return tipo(0) if tipo in (int, float) else ""
            
            # Tratamento especial para strings
            if tipo == str:
                return valor_str
                
            # Conversão numérica
            if tipo == int:
                return int(float(valor_str))  # Converte via float primeiro para lidar com decimais
            elif tipo == float:
                return float(valor_str)
                
        except (ValueError, AttributeError, TypeError) as e:
            logger.debug(f"Erro ao extrair {stat_name}: {e}")
            return tipo(0) if tipo in (int, float) else ""

    def extrair_estatisticas_jogador(self, linha_sum, linha_pass, linha_pass_types, 
                                   linha_def, linha_poss, linha_misc, 
                                   partida_id: int, time_nome: str) -> Optional[EstatisticasJogador]:
        """
        Extrai estatísticas completas de um jogador a partir das linhas das tabelas.
        
        Args:
            linha_sum, linha_pass, linha_pass_types, linha_def, linha_poss, linha_misc: Linhas das respectivas tabelas
            partida_id: ID da partida
            time_nome: Nome do time
            
        Returns:
            EstatisticasJogador or None: Objeto com estatísticas ou None se inválido
        """
        try:
            # Verifica se o jogador jogou
            minutos = self.extrair_stat_seguro(linha_sum, 'minutes', int)
            if minutos == 0:
                return None
                
            jogador_nome = self.extrair_stat_seguro(linha_sum, 'player', str)
            if not jogador_nome:
                return None

            # Cria objeto base
            stats = EstatisticasJogador(
                partida_id=partida_id,
                jogador_nome=jogador_nome,
                time_nome=time_nome
            )

            # Mapeia as tabelas para facilitar a extração
            tabelas_map = {
                'sum': linha_sum,
                'pass': linha_pass,
                'pass_types': linha_pass_types,
                'def': linha_def,
                'poss': linha_poss,
                'misc': linha_misc
            }

            # Extrai todas as estatísticas usando o mapeamento
            for data_stat, (field_name, field_type) in self.stat_mapping.items():
                # Determina qual tabela usar baseado no tipo de estatística
                tabela_key = self._get_table_for_stat(data_stat)
                if tabela_key in tabelas_map:
                    valor = self.extrair_stat_seguro(tabelas_map[tabela_key], data_stat, field_type)
                    setattr(stats, field_name, valor)

            # Cálculos especiais
            stats.xg_npxg_assist_jogador = (
                self.extrair_stat_seguro(linha_sum, 'npxg_plus_xg_assist', float) - 
                stats.npxg_jogador
            )

            return stats

        except Exception as e:
            logger.error(f"Erro ao extrair estatísticas do jogador: {e}")
            return None

    def _get_table_for_stat(self, data_stat: str) -> str:
        """Determina qual tabela contém uma determinada estatística."""
        pass_stats = ['passes_completed', 'passes', 'passes_pct', 'passes_total_distance', 'passes_progressive_distance']
        pass_type_stats = ['passes_completed_short', 'passes_short', 'passes_completed_medium', 'passes_medium', 
                          'passes_completed_long', 'passes_long', 'assisted_shots', 'passes_into_final_third', 
                          'passes_into_penalty_area', 'crosses_into_penalty_area']
        def_stats = ['tackles', 'tackles_won', 'blocks', 'blocked_shots', 'blocked_passes', 'interceptions', 
                    'errors', 'tackles_interceptions']
        poss_stats = ['touches', 'touches_def_3rd', 'touches_mid_3rd', 'touches_att_3rd', 'touches_def_pen_area',
                     'touches_att_pen_area', 'dribbles', 'dribbles_completed', 'dribbles_completed_pct',
                     'progressive_carries', 'progressive_passes_received']
        misc_stats = ['fouls', 'fouled', 'recoveries', 'aerials_won', 'aerials_lost', 'aerials_won_pct']
        
        if data_stat in pass_stats:
            return 'pass'
        elif data_stat in pass_type_stats:
            return 'pass_types'
        elif data_stat in def_stats:
            return 'def'
        elif data_stat in poss_stats:
            return 'poss'
        elif data_stat in misc_stats:
            return 'misc'
        else:
            return 'sum'  # Default para tabela summary

    def processar_match_report(self, soup, partida_id: int, match_url: str = None) -> Tuple[bool, int]:
        """
        Extrai o conjunto completo de estatísticas de jogadores da página.
        
        Args:
            soup: BeautifulSoup object da página
            partida_id: ID da partida
            match_url: URL da partida para coleta de estatísticas avançadas
            
        Returns:
            Tuple[bool, int]: (sucesso, número_de_jogadores_processados)
        """
        jogadores_processados = 0
        
        # Processa estatísticas avançadas se o scraper estiver disponível
        if self.advanced_scraper and match_url:
            try:
                # Obtém estatísticas avançadas
                advanced_stats = self.advanced_scraper.get_advanced_match_stats(match_url)
                
                # Atualiza o banco de dados com as estatísticas avançadas
                if advanced_stats:
                    with self.get_db_connection() as conn:
                        cursor = conn.cursor()
                        
                        # Atualiza estatísticas da partida
                        cursor.execute("""
                            UPDATE estatisticas_partidas 
                            SET xg_casa = ?, xg_visitante = ?, formacao_casa = ?, formacao_visitante = ?
                            WHERE partida_id = ?
                        """, (
                            advanced_stats['expected_goals'].get('xg_casa'),
                            advanced_stats['expected_goals'].get('xg_visitante'),
                            advanced_stats['formacoes'].get('casa'),
                            advanced_stats['formacoes'].get('visitante'),
                            partida_id
                        ))
                        
                        # Atualiza estatísticas de jogadores (xA, etc.)
                        for team in ['home_players', 'away_players']:
                            for player in advanced_stats['jogadores'].get(team, []):
                                cursor.execute("""
                                    UPDATE estatisticas_jogador_partida 
                                    SET xa = ?
                                    WHERE partida_id = ? AND jogador_nome = ?
                                """, (
                                    player.get('xa'),
                                    partida_id,
                                    player.get('nome')
                                ))
                        
                        conn.commit()
                        self.stats['partidas_com_stats_avancados'] += 1
                        logger.info(f"  -> Estatísticas avançadas salvas para a partida {partida_id}")
                        
            except Exception as e:
                logger.error(f"  -> Erro ao processar estatísticas avançadas: {e}")
        
        try:
            # Mapeia o ID da tabela no HTML para o nome do time
            times_mapeados = {}
            for caption in soup.select("table[id*='_summary'] caption"):
                if caption.parent:
                    id_base = caption.parent['id'].replace('_summary', '')
                    time_nome = caption.get_text().replace(" Player Stats Table", "").strip()
                    if time_nome:
                        times_mapeados[id_base] = time_nome

            if not times_mapeados:
                logger.warning("  -> Nenhum time identificado nas tabelas.")
                return False, 0

            # Processa cada time
            for id_base, time_nome in times_mapeados.items():
                logger.debug(f"  -> Processando estatísticas do time: {time_nome}")
                
                # Encontra todas as tabelas de estatísticas para o time atual
                tabelas = {
                    'sum': soup.find('table', id=f'{id_base}_summary'),
                    'pass': soup.find('table', id=f'{id_base}_passing'),
                    'pass_types': soup.find('table', id=f'{id_base}_passing_types'),
                    'def': soup.find('table', id=f'{id_base}_defense'),
                    'poss': soup.find('table', id=f'{id_base}_possession'),
                    'misc': soup.find('table', id=f'{id_base}_misc')
                }
                
                # Verifica se todas as tabelas foram encontradas
                if not all(tabelas.values()):
                    missing = [k for k, v in tabelas.items() if v is None]
                    logger.warning(f"  -> Tabelas ausentes para {time_nome}: {missing}")
                    continue

                # Processa cada jogador
                tbody_sum = tabelas['sum'].find('tbody')
                if not tbody_sum:
                    continue
                    
                linhas_sum = tbody_sum.find_all('tr')
                
                for i, linha_sum in enumerate(linhas_sum):
                    try:
                        # Obtém linhas correspondentes das outras tabelas
                        linhas_outras = {}
                        for tipo, tabela in tabelas.items():
                            if tipo != 'sum':
                                tbody = tabela.find('tbody')
                                if tbody:
                                    todas_linhas = tbody.find_all('tr')
                                    if i < len(todas_linhas):
                                        linhas_outras[tipo] = todas_linhas[i]
                                    else:
                                        logger.warning(f"  -> Linha {i} não encontrada na tabela {tipo}")
                                        linhas_outras[tipo] = None

                        # Verifica se todas as linhas foram encontradas
                        if None in linhas_outras.values():
                            continue

                        # Extrai estatísticas do jogador
                        stats_jogador = self.extrair_estatisticas_jogador(
                            linha_sum, 
                            linhas_outras['pass'],
                            linhas_outras['pass_types'],
                            linhas_outras['def'],
                            linhas_outras['poss'],
                            linhas_outras['misc'],
                            partida_id, 
                            time_nome
                        )

                        if stats_jogador:
                            # Salva no banco de dados
                            if self.salvar_estatisticas_jogador(stats_jogador):
                                jogadores_processados += 1

                    except Exception as e:
                        logger.error(f"  -> Erro ao processar jogador na linha {i}: {e}")
                        continue

            logger.info(f"  -> {jogadores_processados} jogadores processados com sucesso.")
            return jogadores_processados > 0, jogadores_processados

        except Exception as e:
            logger.error(f"  -> Erro geral ao processar match report: {e}")
            return False, 0

    def salvar_estatisticas_jogador(self, stats: EstatisticasJogador) -> bool:
        """
        Salva as estatísticas de um jogador no banco de dados.
        
        Args:
            stats: Objeto com as estatísticas do jogador
            
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Converte para dicionário e prepara query
                dados = stats.to_dict()
                colunas = ', '.join(dados.keys())
                placeholders = ', '.join(['?'] * len(dados))
                
                query = f"""
                    INSERT OR REPLACE INTO estatisticas_jogador_partida 
                    ({colunas}, updated_at) 
                    VALUES ({placeholders}, CURRENT_TIMESTAMP)
                """
                
                cursor.execute(query, tuple(dados.values()))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            logger.error(f"Erro ao salvar estatísticas do jogador {stats.jogador_nome}: {e}")
            return False

    def obter_partidas_pendentes(self) -> List[Tuple[int, str]]:
        """Obtém partidas pendentes de processamento detalhado."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, url_match_report 
                    FROM partidas 
                    WHERE status_coleta_detalhada = 'pendente'
                    ORDER BY id
                """)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter partidas pendentes: {e}")
            return []

    def atualizar_status_partida(self, partida_id: int, status: str) -> None:
        """Atualiza o status de uma partida no banco de dados."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE partidas SET status_coleta_detalhada = ? WHERE id = ?", 
                    (status, partida_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Erro ao atualizar status da partida {partida_id}: {e}")

    async def executar_coleta(self) -> Dict[str, int]:
        """
        Executa o processo completo de coleta de estatísticas detalhadas.
        
        Returns:
            Dict[str, int]: Estatísticas da execução
        """
        logger.info("Iniciando coleta de estatísticas detalhadas...")
        
        # Obtém partidas pendentes
        partidas = self.obter_partidas_pendentes()
        total_partidas = len(partidas)
        
        if not partidas:
            logger.info("Nenhuma partida pendente para processamento.")
            return self.stats
            
        logger.info(f"Encontradas {total_partidas} partidas para processar.")
        
        # Configura a barra de progresso
        with tqdm(total=total_partidas, desc="Processando partidas") as pbar:
            for partida in partidas:
                partida_id, url = partida
                
                try:
                    # Atualiza status para 'processando'
                    self.atualizar_status_partida(partida_id, 'processando')
                    
                    # Faz a requisição e processa a página
                    soup = fazer_requisicao(url)
                    if not soup:
                        logger.warning(f"  -> Falha ao obter a página da partida {partida_id}")
                        self.atualizar_status_partida(partida_id, 'erro')
                        self.stats['partidas_com_erro'] += 1
                        continue
                    
                    # Processa as estatísticas da partida
                    sucesso, num_jogadores = self.processar_match_report(soup, partida_id, url)
                    
                    if sucesso and num_jogadores > 0:
                        self.atualizar_status_partida(partida_id, 'concluido')
                        self.stats['partidas_processadas'] += 1
                        self.stats['jogadores_processados'] += num_jogadores
                        logger.info(f"  -> Partida {partida_id} processada com sucesso ({num_jogadores} jogadores)")
                    else:
                        self.atualizar_status_partida(partida_id, 'sem_stats')
                        self.stats['partidas_sem_stats'] += 1
                        logger.warning(f"  -> Nenhuma estatística encontrada para a partida {partida_id}")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar partida {partida_id}: {e}")
                    logger.error(traceback.format_exc())
                    self.atualizar_status_partida(partida_id, 'erro')
                    self.stats['partidas_com_erro'] += 1
                
                # Atualiza a barra de progresso
                pbar.update(1)
                
                # Pequena pausa para evitar sobrecarga
                time.sleep(1)
        
        logger.info("Coleta de estatísticas concluída.")
        return self.stats


def main():
    """Função principal para execução standalone do módulo."""
    try:
        # Garantir que o diretório do banco existe
        os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
        
        # Executar coleta
        coletor = ColetorEstatisticas()
        stats = coletor.executar_coleta()
        
        # Limpar recursos
        limpar_recursos()
        
        return stats
        
    except Exception as e:
        logger.critical(f"Erro crítico na execução principal: {e}", exc_info=True)
        return None
    finally:
        # Garantir limpeza de recursos
        limpar_recursos()


if __name__ == "__main__":
    main()