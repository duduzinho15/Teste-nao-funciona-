import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('teste_scraper_operario_criciuma.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdvancedMatchScraper:
    """Classe para extrair estatísticas avançadas de partidas do FBRef."""
    
    def __init__(self, session):
        self.session = session
        self.base_url = "https://fbref.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def fetch_page(self, url):
        """Busca o conteúdo da página."""
        try:
            logger.info(f"Acessando URL: {url}")
            async with self.session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logger.error(f"Erro ao acessar a página {url}: {str(e)}")
            return None
    
    async def extract_match_stats(self, match_url):
        """Extrai estatísticas básicas de uma partida."""
        try:
            # Acessa a página da partida
            match_html = await self.fetch_page(match_url)
            if not match_html:
                logger.error("Falha ao obter o conteúdo da página.")
                return None
            
            # Salva o HTML para análise
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(match_html)
            logger.info("Página salva como 'debug_page.html' para análise")
            
            soup = BeautifulSoup(match_html, 'html.parser')
            
            # Inicializa o dicionário de estatísticas
            stats = {
                'url': match_url,
                'home_team': 'Desconhecido',
                'away_team': 'Desconhecido',
                'score': '0-0',
                'stats': {}
            }
            
            try:
                # Extrai o título da página
                title = soup.find('title')
                if title:
                    title_text = title.get_text(strip=True)
                    # Tenta extrair times do título
                    match = re.search(r'(.+?)\s+vs\.?\s+(.+?)(?:\s+Match Report|\s+\|)', title_text)
                    if match:
                        stats['home_team'] = match.group(1).strip()
                        stats['away_team'] = match.group(2).strip()
                
                # Encontra a seção de estatísticas da partida
                scorebox = soup.find('div', {'class': 'scorebox'})
                if scorebox:
                    # Tenta extrair os times diretamente dos links das equipes
                    team_links = scorebox.find_all('a', {'itemprop': 'name'})
                    if len(team_links) >= 2:
                        stats['home_team'] = team_links[0].get_text(strip=True)
                        stats['away_team'] = team_links[1].get_text(strip=True)
                    
                    # Tenta extrair o placar
                    score_div = scorebox.find('div', {'class': 'scores'})
                    if score_div:
                        stats['score'] = score_div.get_text(strip=True)
                
                logger.info(f"Partida: {stats['home_team']} {stats['score']} {stats['away_team']}")
                
                # Tenta extrair estatísticas básicas
                stats_section = soup.find('div', {'id': 'team_stats'})
                if stats_section:
                    # Extrai posse de bola
                    possession_div = stats_section.find('div', string=re.compile(r'Possession', re.IGNORECASE))
                    if possession_div:
                        possession_values = possession_div.find_next('div').find_all('div')
                        if len(possession_values) >= 2:
                            stats['stats']['home_possession'] = possession_values[0].get_text(strip=True)
                            stats['stats']['away_possession'] = possession_values[1].get_text(strip=True)
                    
                    # Extrai finalizações
                    shots_div = stats_section.find('div', string=re.compile(r'Shots', re.IGNORECASE))
                    if shots_div:
                        shots_values = shots_div.find_next('div').find_all('div')
                        if len(shots_values) >= 2:
                            stats['stats']['home_shots'] = shots_values[0].get_text(strip=True)
                            stats['stats']['away_shots'] = shots_values[1].get_text(strip=True)
                    
                    # Extrai finalizações no alvo
                    shots_on_target_div = stats_section.find('div', string=re.compile(r'Shots on Target', re.IGNORECASE))
                    if not shots_on_target_div:
                        shots_on_target_div = stats_section.find('div', string=re.compile(r'On Target', re.IGNORECASE))
                    
                    if shots_on_target_div:
                        sot_values = shots_on_target_div.find_next('div').find_all('div')
                        if len(sot_values) >= 2:
                            stats['stats']['home_shots_on_target'] = sot_values[0].get_text(strip=True)
                            stats['stats']['away_shots_on_target'] = sot_values[1].get_text(strip=True)
                    
                    # Extrai escanteios
                    corners_div = stats_section.find('div', string=re.compile(r'Corners', re.IGNORECASE))
                    if corners_div:
                        corners_values = corners_div.find_next('div').find_all('div')
                        if len(corners_values) >= 2:
                            stats['stats']['home_corners'] = corners_values[0].get_text(strip=True)
                            stats['stats']['away_corners'] = corners_values[1].get_text(strip=True)
                
                # Tenta extrair formações táticas
                lineups = soup.find_all('div', {'class': 'lineup'})
                if len(lineups) >= 2:
                    stats['stats']['home_formation'] = lineups[0].get_text(strip=True).replace('Formation:', '').strip()
                    stats['stats']['away_formation'] = lineups[1].get_text(strip=True).replace('Formation:', '').strip()
                
                # Tenta extrair xG se disponível
                xg_div = soup.find('div', string=re.compile(r'xG', re.IGNORECASE))
                if xg_div:
                    xg_values = xg_div.find_next('div').find_all('div')
                    if len(xg_values) >= 2:
                        stats['stats']['home_xg'] = xg_values[0].get_text(strip=True)
                        stats['stats']['away_xg'] = xg_values[1].get_text(strip=True)
                
                logger.info("Estatísticas extraídas com sucesso!")
                
            except Exception as e:
                logger.error(f"Erro ao extrair estatísticas: {str(e)}")
                # Continua mesmo com erro para retornar o que foi possível extrair
            
            return stats if stats['stats'] else None
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao extrair estatísticas da partida: {str(e)}")
            return None

async def main():
    # URL da partida fornecida
    match_url = "https://fbref.com/en/matches/0b52e9a9/Operario-Criciuma-August-1-2025-Serie-B"
    
    # Configuração da sessão HTTP
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        scraper = AdvancedMatchScraper(session)
        
        logger.info("Iniciando extração de estatísticas avançadas...")
        start_time = datetime.now()
        
        # Extrai as estatísticas da partida
        match_stats = await scraper.extract_match_stats(match_url)
        
        end_time = datetime.now()
        logger.info(f"Tempo total de execução: {(end_time - start_time).total_seconds():.2f} segundos")
        
        # Exibe os resultados
        if match_stats:
            print("\n=== ESTATÍSTICAS DA PARTIDA ===")
            print(f"{match_stats['home_team']} {match_stats['score']} {match_stats['away_team']}")
            print(f"URL: {match_stats['url']}")
            
            print("\n=== ESTATÍSTICAS AVANÇADAS ===")
            for key, value in match_stats['stats'].items():
                print(f"{key}: {value}")
        else:
            print("Não foi possível extrair as estatísticas da partida.")

if __name__ == "__main__":
    asyncio.run(main())
