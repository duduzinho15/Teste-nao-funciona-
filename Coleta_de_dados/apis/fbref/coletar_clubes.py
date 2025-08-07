"""
Módulo para coleta de dados de clubes do FBRef.
Coleta informações de clubes, separando masculino e feminino, e suas estatísticas.
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
class ClubeInfo:
    """Classe para estruturar informações de um clube."""
    nome: str
    pais: str
    genero: str  # M ou F
    url_clube: str
    url_records_vs_opponents: Optional[str] = None

@dataclass
class PaisInfo:
    """Classe para estruturar informações de um país."""
    nome: str
    codigo: str
    url_clubes: str
    url_jogadores: str

class ColetorClubes:
    """Classe principal para coleta de dados de clubes."""
    
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self.stats = {
            'paises_processados': 0,
            'clubes_encontrados': 0,
            'clubes_masculino': 0,
            'clubes_feminino': 0,
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

    def setup_database_clubes(self) -> None:
        """Cria as tabelas necessárias para armazenar dados de clubes."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de países
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS paises_clubes (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    codigo TEXT UNIQUE,
                    url_clubes TEXT,
                    url_jogadores TEXT,
                    status_coleta TEXT DEFAULT 'pendente'
                )
            ''')
            
            # Tabela de clubes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clubes (
                    id INTEGER PRIMARY KEY,
                    pais_id INTEGER,
                    nome TEXT NOT NULL,
                    genero TEXT CHECK(genero IN ('M', 'F')),
                    url_clube TEXT UNIQUE,
                    url_records_vs_opponents TEXT,
                    status_coleta TEXT DEFAULT 'pendente',
                    status_records TEXT DEFAULT 'pendente',
                    FOREIGN KEY (pais_id) REFERENCES paises_clubes (id)
                )
            ''')
            
            # Tabela de estatísticas de clubes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estatisticas_clube (
                    id INTEGER PRIMARY KEY,
                    clube_id INTEGER,
                    temporada TEXT,
                    competicao TEXT,
                    jogos INTEGER,
                    vitorias INTEGER,
                    empates INTEGER,
                    derrotas INTEGER,
                    gols_marcados INTEGER,
                    gols_sofridos INTEGER,
                    pontos INTEGER,
                    posicao INTEGER,
                    FOREIGN KEY (clube_id) REFERENCES clubes (id)
                )
            ''')
            
            # Tabela de records vs opponents
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records_vs_opponents (
                    id INTEGER PRIMARY KEY,
                    clube_id INTEGER,
                    adversario TEXT,
                    jogos INTEGER,
                    vitorias INTEGER,
                    empates INTEGER,
                    derrotas INTEGER,
                    gols_marcados INTEGER,
                    gols_sofridos INTEGER,
                    ultima_partida TEXT,
                    FOREIGN KEY (clube_id) REFERENCES clubes (id)
                )
            ''')
            
            conn.commit()
            logger.info("Tabelas de clubes criadas/verificadas com sucesso.")

    def coletar_paises_clubes(self) -> List[PaisInfo]:
        """
        Coleta a lista de países com clubes do FBRef.
        
        Returns:
            List[PaisInfo]: Lista de países encontrados
        """
        logger.info("Coletando lista de países com clubes...")
        
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
                
                # Constrói URLs
                url_clubes = f"{BASE_URL}{href}"
                url_jogadores = f"{BASE_URL}/en/country/players/{codigo_pais}/Brazil-Football-Players"
                
                paises.append(PaisInfo(
                    nome=nome_pais,
                    codigo=codigo_pais,
                    url_clubes=url_clubes,
                    url_jogadores=url_jogadores
                ))
                
            except Exception as e:
                logger.debug(f"Erro ao processar linha de país: {e}")
                continue
        
        logger.info(f"Encontrados {len(paises)} países com clubes")
        return paises

    def coletar_clubes_do_pais(self, pais: PaisInfo) -> List[ClubeInfo]:
        """
        Coleta os clubes de um país específico.
        
        Args:
            pais: Informações do país
            
        Returns:
            List[ClubeInfo]: Lista de clubes encontrados
        """
        logger.info(f"Coletando clubes do país: {pais.nome}")
        
        soup = fazer_requisicao(pais.url_clubes)
        if not soup:
            logger.error(f"Falha ao obter página de clubes de {pais.nome}")
            return []
        
        clubes = []
        
        # Procura pela tabela de clubes
        tabela_clubes = soup.find('table', class_='stats_table')
        if not tabela_clubes:
            logger.error(f"Tabela de clubes não encontrada para {pais.nome}")
            return []
        
        tbody = tabela_clubes.find('tbody')
        if not tbody:
            logger.error(f"Corpo da tabela de clubes não encontrado para {pais.nome}")
            return []
        
        for linha in tbody.find_all('tr'):
            try:
                # Procura pelo link do clube
                link_clube = linha.find('a')
                if not link_clube or not link_clube.get('href'):
                    continue
                
                href = link_clube.get('href')
                if not href.startswith('/en/squads/'):
                    continue
                
                # Extrai nome do clube
                nome_clube = link_clube.get_text(strip=True)
                
                # Procura pela coluna de gênero
                genero = "M"  # Padrão masculino
                cols = linha.find_all('td')
                for col in cols:
                    if col.get('data-stat') == 'gender':
                        genero_text = col.get_text(strip=True)
                        if genero_text == 'F':
                            genero = "F"
                        break
                
                # Constrói URL do clube
                url_clube = f"{BASE_URL}{href}"
                
                # Procura pelo link "Records vs Opponents"
                url_records = None
                for col in cols:
                    links = col.find_all('a')
                    for link in links:
                        if 'Records vs Opponents' in link.get_text():
                            url_records = f"{BASE_URL}{link.get('href')}"
                            break
                    if url_records:
                        break
                
                clubes.append(ClubeInfo(
                    nome=nome_clube,
                    pais=pais.nome,
                    genero=genero,
                    url_clube=url_clube,
                    url_records_vs_opponents=url_records
                ))
                
            except Exception as e:
                logger.debug(f"Erro ao processar linha de clube: {e}")
                continue
        
        logger.info(f"Encontrados {len(clubes)} clubes em {pais.nome}")
        return clubes

    def salvar_pais_no_banco(self, pais: PaisInfo) -> int:
        """
        Salva um país no banco de dados.
        
        Args:
            pais: Informações do país
            
        Returns:
            int: ID do país salvo
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO paises_clubes (nome, codigo, url_clubes, url_jogadores)
                VALUES (?, ?, ?, ?)
            """, (pais.nome, pais.codigo, pais.url_clubes, pais.url_jogadores))
            
            cursor.execute("SELECT id FROM paises_clubes WHERE codigo = ?", (pais.codigo,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                logger.error(f"Falha ao obter ID do país: {pais.nome}")
                return None

    def salvar_clube_no_banco(self, clube: ClubeInfo, pais_id: int) -> int:
        """
        Salva um clube no banco de dados.
        
        Args:
            clube: Informações do clube
            pais_id: ID do país
            
        Returns:
            int: ID do clube salvo
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO clubes (pais_id, nome, genero, url_clube, url_records_vs_opponents)
                VALUES (?, ?, ?, ?, ?)
            """, (pais_id, clube.nome, clube.genero, clube.url_clube, clube.url_records_vs_opponents))
            
            cursor.execute("SELECT id FROM clubes WHERE url_clube = ?", (clube.url_clube,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                logger.error(f"Falha ao obter ID do clube: {clube.nome}")
                return None

    def executar_coleta_completa(self) -> Dict[str, int]:
        """
        Executa a coleta completa de clubes.
        
        Returns:
            Dict com estatísticas da coleta
        """
        logger.info("🚀 Iniciando coleta completa de clubes...")
        
        # Configura banco de dados
        self.setup_database_clubes()
        
        # Coleta países
        paises = self.coletar_paises_clubes()
        if not paises:
            logger.error("Nenhum país encontrado")
            return self.stats
        
        # Processa cada país
        for pais in tqdm(paises, desc="Processando países"):
            try:
                # Salva país no banco
                pais_id = self.salvar_pais_no_banco(pais)
                if not pais_id:
                    continue
                
                # Coleta clubes do país
                clubes = self.coletar_clubes_do_pais(pais)
                
                # Salva clubes no banco
                for clube in clubes:
                    try:
                        clube_id = self.salvar_clube_no_banco(clube, pais_id)
                        if clube_id:
                            self.stats['clubes_encontrados'] += 1
                            if clube.genero == 'M':
                                self.stats['clubes_masculino'] += 1
                            else:
                                self.stats['clubes_feminino'] += 1
                    except Exception as e:
                        logger.error(f"Erro ao salvar clube {clube.nome}: {e}")
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
        
        logger.info("✅ Coleta de clubes finalizada!")
        return self.stats

    def gerar_relatorio_final(self) -> None:
        """Gera relatório final da coleta de clubes."""
        logger.info("\n" + "="*80)
        logger.info("📊 RELATÓRIO FINAL - COLETA DE CLUBES")
        logger.info("="*80)
        logger.info(f"🌍 Países processados: {self.stats['paises_processados']}")
        logger.info(f"🏟️  Clubes encontrados: {self.stats['clubes_encontrados']}")
        logger.info(f"👨 Clubes masculino: {self.stats['clubes_masculino']}")
        logger.info(f"👩 Clubes feminino: {self.stats['clubes_feminino']}")
        logger.info(f"❌ Erros de processamento: {self.stats['erros_processamento']}")
        logger.info("="*80)

def main():
    """Função principal para execução standalone."""
    coletor = ColetorClubes()
    stats = coletor.executar_coleta_completa()
    
    logger.info(f"\n📊 Estatísticas finais:")
    logger.info(f"  - Países processados: {stats['paises_processados']}")
    logger.info(f"  - Clubes encontrados: {stats['clubes_encontrados']}")
    logger.info(f"  - Erros: {stats['erros_processamento']}")
    
    return stats

if __name__ == "__main__":
    main() 