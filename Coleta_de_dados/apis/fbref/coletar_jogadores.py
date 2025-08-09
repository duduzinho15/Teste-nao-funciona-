"""
Módulo para coleta de dados de jogadores do FBRef.
Coleta informações de jogadores de todos os países e suas estatísticas detalhadas.
"""

import logging
import sqlite3
import os
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from contextlib import contextmanager
from tqdm import tqdm

from .fbref_utils import fazer_requisicao, BASE_URL

# Configurações
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')

logger = logging.getLogger(__name__)

@dataclass
class JogadorInfo:
    """Classe para estruturar informações de um jogador."""
    nome: str
    pais: str
    url_jogador: str
    url_all_competitions: Optional[str] = None
    url_domestic_leagues: Optional[str] = None
    url_domestic_cups: Optional[str] = None
    url_international_cups: Optional[str] = None
    url_national_team: Optional[str] = None

@dataclass
class PaisJogadoresInfo:
    """Classe para estruturar informações de um país para jogadores."""
    nome: str
    codigo: str
    url_jogadores: str

class ColetorJogadores:
    """Classe principal para coleta de dados de jogadores."""
    
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self.stats = {
            'paises_processados': 0,
            'jogadores_encontrados': 0,
            'jogadores_com_stats': 0,
            'erros_processamento': 0
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

    def setup_database_jogadores(self) -> None:
        """Cria as tabelas necessárias para armazenar dados de jogadores."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de países para jogadores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS paises_jogadores (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    codigo TEXT UNIQUE,
                    url_jogadores TEXT,
                    status_coleta TEXT DEFAULT 'pendente'
                )
            ''')
            
            # Tabela de jogadores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jogadores (
                    id INTEGER PRIMARY KEY,
                    pais_id INTEGER,
                    nome TEXT NOT NULL,
                    url_jogador TEXT UNIQUE,
                    url_all_competitions TEXT,
                    url_domestic_leagues TEXT,
                    url_domestic_cups TEXT,
                    url_international_cups TEXT,
                    url_national_team TEXT,
                    status_coleta TEXT DEFAULT 'pendente',
                    status_stats TEXT DEFAULT 'pendente',
                    FOREIGN KEY (pais_id) REFERENCES paises_jogadores (id)
                )
            ''')
            
            # Tabela de estatísticas gerais de jogadores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estatisticas_jogador_geral (
                    id INTEGER PRIMARY KEY,
                    jogador_id INTEGER,
                    temporada TEXT,
                    competicao TEXT,
                    time TEXT,
                    jogos INTEGER,
                    jogos_titular INTEGER,
                    minutos INTEGER,
                    gols INTEGER,
                    assistencias INTEGER,
                    cartoes_amarelos INTEGER,
                    cartoes_vermelhos INTEGER,
                    FOREIGN KEY (jogador_id) REFERENCES jogadores (id)
                )
            ''')
            
            # Tabela de estatísticas por tipo de competição
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estatisticas_jogador_competicao (
                    id INTEGER PRIMARY KEY,
                    jogador_id INTEGER,
                    tipo_competicao TEXT, -- 'all', 'domestic_leagues', 'domestic_cups', 'international_cups', 'national_team'
                    temporada TEXT,
                    competicao TEXT,
                    time TEXT,
                    jogos INTEGER,
                    jogos_titular INTEGER,
                    minutos INTEGER,
                    gols INTEGER,
                    assistencias INTEGER,
                    cartoes_amarelos INTEGER,
                    cartoes_vermelhos INTEGER,
                    FOREIGN KEY (jogador_id) REFERENCES jogadores (id)
                )
            ''')
            
            conn.commit()
            logger.info("Tabelas de jogadores criadas/verificadas com sucesso.")

    def coletar_paises_jogadores(self) -> List[PaisJogadoresInfo]:
        """
        Coleta a lista de países com jogadores do FBRef.
        
        Returns:
            List[PaisJogadoresInfo]: Lista de países encontrados
        """
        logger.info("Coletando lista de países com jogadores...")
        
        # Usa a mesma página de squads para obter países
        url_paises = f"{BASE_URL}/en/squads/"
        soup = fazer_requisicao(url_paises)
        if not soup:
            logger.error("Falha ao obter página de países")
            return []
        
        paises = []
        
        # Procura pela tabela de países
        tabela_paises = soup.find('table', class_='stats_table')
        if not tabela_paises:
            logger.error("Tabela de países não encontrada")
            return []
        
        tbody = tabela_paises.find('tbody')
        if not tbody:
            logger.error("Corpo da tabela de países não encontrado")
            return []
        
        for linha in tbody.find_all('tr'):
            try:
                # Procura pelo link do país
                link_pais = linha.find('a')
                if not link_pais or not link_pais.get('href'):
                    continue
                
                href = link_pais.get('href')
                if not href.startswith('/en/country/clubs/'):
                    continue
                
                # Extrai informações do país
                nome_pais = link_pais.get_text(strip=True)
                codigo_pais = href.split('/')[-2] if len(href.split('/')) > 4 else ""
                
                # Constrói URL de jogadores
                url_jogadores = f"{BASE_URL}/en/country/players/{codigo_pais}/{nome_pais.replace(' ', '-')}-Football-Players"
                
                paises.append(PaisJogadoresInfo(
                    nome=nome_pais,
                    codigo=codigo_pais,
                    url_jogadores=url_jogadores
                ))
                
            except Exception as e:
                logger.debug(f"Erro ao processar linha de país: {e}")
                continue
        
        logger.info(f"Encontrados {len(paises)} países com jogadores")
        return paises

    def coletar_jogadores_do_pais(self, pais: PaisJogadoresInfo) -> List[JogadorInfo]:
        """
        Coleta os jogadores de um país específico.
        
        Args:
            pais: Informações do país
            
        Returns:
            List[JogadorInfo]: Lista de jogadores encontrados
        """
        logger.info(f"Coletando jogadores do país: {pais.nome}")
        
        soup = fazer_requisicao(pais.url_jogadores)
        if not soup:
            logger.error(f"Falha ao obter página de jogadores de {pais.nome}")
            return []
        
        jogadores = []
        
        # Procura pela tabela de jogadores
        tabela_jogadores = soup.find('table', class_='stats_table')
        if not tabela_jogadores:
            logger.error(f"Tabela de jogadores não encontrada para {pais.nome}")
            return []
        
        tbody = tabela_jogadores.find('tbody')
        if not tbody:
            logger.error(f"Corpo da tabela de jogadores não encontrado para {pais.nome}")
            return []
        
        for linha in tbody.find_all('tr'):
            try:
                # Procura pelo link do jogador
                link_jogador = linha.find('a')
                if not link_jogador or not link_jogador.get('href'):
                    continue
                
                href = link_jogador.get('href')
                if not href.startswith('/en/players/'):
                    continue
                
                # Extrai nome do jogador
                nome_jogador = link_jogador.get_text(strip=True)
                
                # Constrói URL do jogador
                url_jogador = f"{BASE_URL}{href}"
                
                # Constrói URLs das páginas de estatísticas
                player_id = href.split('/')[3]  # Extrai o ID do jogador da URL
                url_all_competitions = f"{BASE_URL}/en/players/{player_id}/all_comps/{nome_jogador.replace(' ', '-')}-Stats---All-Competitions"
                url_domestic_leagues = f"{BASE_URL}/en/players/{player_id}/dom_lg/{nome_jogador.replace(' ', '-')}-Domestic-League-Stats"
                url_domestic_cups = f"{BASE_URL}/en/players/{player_id}/dom_cup/{nome_jogador.replace(' ', '-')}-Domestic-Cup-Stats"
                url_international_cups = f"{BASE_URL}/en/players/{player_id}/intl_cup/{nome_jogador.replace(' ', '-')}-International-Cup-Stats"
                url_national_team = f"{BASE_URL}/en/players/{player_id}/nat_tm/{nome_jogador.replace(' ', '-')}-National-Team-Stats"
                
                jogadores.append(JogadorInfo(
                    nome=nome_jogador,
                    pais=pais.nome,
                    url_jogador=url_jogador,
                    url_all_competitions=url_all_competitions,
                    url_domestic_leagues=url_domestic_leagues,
                    url_domestic_cups=url_domestic_cups,
                    url_international_cups=url_international_cups,
                    url_national_team=url_national_team
                ))
                
            except Exception as e:
                logger.debug(f"Erro ao processar linha de jogador: {e}")
                continue
        
        logger.info(f"Encontrados {len(jogadores)} jogadores em {pais.nome}")
        return jogadores

    def salvar_pais_jogadores_no_banco(self, pais: PaisJogadoresInfo) -> int:
        """
        Salva um país de jogadores no banco de dados.
        
        Args:
            pais: Informações do país
            
        Returns:
            int: ID do país salvo
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO paises_jogadores (nome, codigo, url_jogadores)
                VALUES (?, ?, ?)
            """, (pais.nome, pais.codigo, pais.url_jogadores))
            
            cursor.execute("SELECT id FROM paises_jogadores WHERE codigo = ?", (pais.codigo,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                logger.error(f"Falha ao obter ID do país: {pais.nome}")
                return None

    def salvar_jogador_no_banco(self, jogador: JogadorInfo, pais_id: int) -> int:
        """
        Salva um jogador no banco de dados.
        
        Args:
            jogador: Informações do jogador
            pais_id: ID do país
            
        Returns:
            int: ID do jogador salvo
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO jogadores (
                    pais_id, nome, url_jogador, url_all_competitions, 
                    url_domestic_leagues, url_domestic_cups, 
                    url_international_cups, url_national_team
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pais_id, jogador.nome, jogador.url_jogador,
                jogador.url_all_competitions, jogador.url_domestic_leagues,
                jogador.url_domestic_cups, jogador.url_international_cups,
                jogador.url_national_team
            ))
            
            cursor.execute("SELECT id FROM jogadores WHERE url_jogador = ?", (jogador.url_jogador,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                logger.error(f"Falha ao obter ID do jogador: {jogador.nome}")
                return None

    def executar_coleta_completa(self) -> Dict[str, int]:
        """
        Executa a coleta completa de jogadores.
        
        Returns:
            Dict com estatísticas da coleta
        """
        logger.info("🚀 Iniciando coleta completa de jogadores...")
        
        # Configura banco de dados
        self.setup_database_jogadores()
        
        # Coleta países
        paises = self.coletar_paises_jogadores()
        if not paises:
            logger.error("Nenhum país encontrado")
            return self.stats
        
        # Processa cada país
        for pais in tqdm(paises, desc="Processando países"):
            try:
                # Salva país no banco
                pais_id = self.salvar_pais_jogadores_no_banco(pais)
                if not pais_id:
                    continue
                
                # Coleta jogadores do país
                jogadores = self.coletar_jogadores_do_pais(pais)
                
                # Salva jogadores no banco
                for jogador in jogadores:
                    try:
                        jogador_id = self.salvar_jogador_no_banco(jogador, pais_id)
                        if jogador_id:
                            self.stats['jogadores_encontrados'] += 1
                    except Exception as e:
                        logger.error(f"Erro ao salvar jogador {jogador.nome}: {e}")
                        self.stats['erros_processamento'] += 1
                
                self.stats['paises_processados'] += 1
                
                # Pausa para evitar sobrecarga
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao processar país {pais.nome}: {e}")
                self.stats['erros_processamento'] += 1
                continue
        
        # Gera relatório final
        self.gerar_relatorio_final()
        
        logger.info("✅ Coleta de jogadores finalizada!")
        return self.stats

    def gerar_relatorio_final(self) -> None:
        """Gera relatório final da coleta de jogadores."""
        logger.info("\n" + "="*80)
        logger.info("📊 RELATÓRIO FINAL - COLETA DE JOGADORES")
        logger.info("="*80)
        logger.info(f"🌍 Países processados: {self.stats['paises_processados']}")
        logger.info(f"⚽ Jogadores encontrados: {self.stats['jogadores_encontrados']}")
        logger.info(f"📈 Jogadores com estatísticas: {self.stats['jogadores_com_stats']}")
        logger.info(f"❌ Erros de processamento: {self.stats['erros_processamento']}")
        logger.info("="*80)

def main():
    """Função principal para execução standalone."""
    coletor = ColetorJogadores()
    stats = coletor.executar_coleta_completa()
    
    logger.info(f"\n📊 Estatísticas finais:")
    logger.info(f"  - Países processados: {stats['paises_processados']}")
    logger.info(f"  - Jogadores encontrados: {stats['jogadores_encontrados']}")
    logger.info(f"  - Erros: {stats['erros_processamento']}")
    
    return stats

if __name__ == "__main__":
    main() 