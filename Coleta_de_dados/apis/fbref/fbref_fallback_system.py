#!/usr/bin/env python3
"""
Sistema de fallback para quando o FBRef está bloqueando requisições.
Utiliza dados locais e cache para continuar funcionando.
"""
import logging
import os
import json
import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FBRefFallbackSystem:
    """Sistema de fallback para dados do FBRef quando o site está inacessível."""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.cache_dir = os.path.join(project_root, "cache_fbref")
        self.db_path = os.path.join(project_root, "Banco_de_dados", "aposta.db")
        self.fallback_data_file = os.path.join(self.cache_dir, "fallback_competitions.json")
        
        # Criar diretório de cache se não existir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Dados de fallback com competições principais
        self.fallback_competitions = [
            {
                "nome": "Premier League",
                "contexto": "Masculino",
                "url": "https://fbref.com/en/comps/9/history/Premier-League-Seasons"
            },
            {
                "nome": "La Liga",
                "contexto": "Masculino", 
                "url": "https://fbref.com/en/comps/12/history/La-Liga-Seasons"
            },
            {
                "nome": "Serie A",
                "contexto": "Masculino",
                "url": "https://fbref.com/en/comps/11/history/Serie-A-Seasons"
            },
            {
                "nome": "Bundesliga",
                "contexto": "Masculino",
                "url": "https://fbref.com/en/comps/20/history/Bundesliga-Seasons"
            },
            {
                "nome": "Ligue 1",
                "contexto": "Masculino",
                "url": "https://fbref.com/en/comps/13/history/Ligue-1-Seasons"
            },
            {
                "nome": "Champions League",
                "contexto": "Masculino",
                "url": "https://fbref.com/en/comps/8/history/Champions-League-Seasons"
            },
            {
                "nome": "Europa League",
                "contexto": "Masculino",
                "url": "https://fbref.com/en/comps/19/history/Europa-League-Seasons"
            },
            {
                "nome": "World Cup",
                "contexto": "Masculino",
                "url": "https://fbref.com/en/comps/1/history/World-Cup-Seasons"
            },
            {
                "nome": "Premier League",
                "contexto": "Feminino",
                "url": "https://fbref.com/en/comps/182/history/Womens-Super-League-Seasons"
            },
            {
                "nome": "Serie A (W)",
                "contexto": "Feminino",
                "url": "https://fbref.com/en/comps/106/history/Serie-A-Seasons"
            }
        ]
    
    def save_fallback_data(self):
        """Salva dados de fallback no arquivo local."""
        try:
            with open(self.fallback_data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "competitions": self.fallback_competitions
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"Dados de fallback salvos em: {self.fallback_data_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar dados de fallback: {e}")
    
    def load_fallback_data(self) -> List[Dict[str, str]]:
        """Carrega dados de fallback do arquivo local."""
        try:
            if os.path.exists(self.fallback_data_file):
                with open(self.fallback_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Dados de fallback carregados: {len(data.get('competitions', []))} competições")
                    return data.get('competitions', [])
        except Exception as e:
            logger.error(f"Erro ao carregar dados de fallback: {e}")
        
        # Se não conseguir carregar, usa dados padrão
        logger.info("Usando dados de fallback padrão")
        return self.fallback_competitions
    
    def get_cached_competitions(self) -> Optional[List[Dict[str, str]]]:
        """Obtém competições do cache local se disponível e válido."""
        cache_file = os.path.join(self.cache_dir, "competitions_cache.json")
        
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # Verifica se o cache é válido (menos de 24 horas)
                cache_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
                if datetime.now() - cache_time < timedelta(hours=24):
                    logger.info(f"Cache válido encontrado: {len(cache_data.get('competitions', []))} competições")
                    return cache_data.get('competitions', [])
                else:
                    logger.info("Cache expirado, será necessário atualizar")
        except Exception as e:
            logger.debug(f"Erro ao verificar cache: {e}")
        
        return None
    
    def save_competitions_cache(self, competitions: List[Dict[str, str]]):
        """Salva competições no cache local."""
        cache_file = os.path.join(self.cache_dir, "competitions_cache.json")
        
        try:
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "competitions": competitions
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Cache atualizado: {len(competitions)} competições salvas")
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
    
    def check_database_status(self) -> Dict[str, Any]:
        """Verifica o status atual do banco de dados."""
        status = {
            "database_exists": False,
            "competitions_count": 0,
            "seasons_count": 0,
            "matches_count": 0,
            "last_update": None
        }
        
        try:
            if os.path.exists(self.db_path):
                status["database_exists"] = True
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Conta competições
                    try:
                        cursor.execute("SELECT COUNT(*) FROM competicoes")
                        status["competitions_count"] = cursor.fetchone()[0]
                    except:
                        pass
                    
                    # Conta temporadas
                    try:
                        cursor.execute("SELECT COUNT(*) FROM links_temporadas")
                        status["seasons_count"] = cursor.fetchone()[0]
                    except:
                        pass
                    
                    # Conta partidas
                    try:
                        cursor.execute("SELECT COUNT(*) FROM partidas")
                        status["matches_count"] = cursor.fetchone()[0]
                    except:
                        pass
                    
                    # Última atualização
                    try:
                        cursor.execute("SELECT MAX(data_criacao) FROM competicoes")
                        last_update = cursor.fetchone()[0]
                        if last_update:
                            status["last_update"] = last_update
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Erro ao verificar status do banco: {e}")
        
        return status
    
    def get_fallback_seasons(self, competition_url: str) -> List[Dict[str, str]]:
        """Gera temporadas de fallback baseadas na URL da competição."""
        seasons = []
        
        # Extrai informações da URL para gerar temporadas apropriadas
        if "Premier-League" in competition_url:
            # Premier League: 1992-2024 (33 temporadas)
            for year in range(1992, 2025):
                season_name = f"{year}-{str(year + 1)[-2:]}"
                seasons.append({
                    "url": f"https://fbref.com/en/comps/9/{season_name}/schedule/{season_name}-Premier-League-Scores-and-Fixtures",
                    "season": season_name,
                    "year": str(year)
                })
                
        elif "La-Liga" in competition_url:
            # La Liga: 1929-2024 (95 temporadas, mas vamos usar as mais recentes)
            for year in range(1990, 2025):
                season_name = f"{year}-{str(year + 1)[-2:]}"
                seasons.append({
                    "url": f"https://fbref.com/en/comps/12/{season_name}/schedule/{season_name}-La-Liga-Scores-and-Fixtures",
                    "season": season_name,
                    "year": str(year)
                })
                
        elif "Serie-A" in competition_url:
            # Serie A: 1929-2024 (95 temporadas, mas vamos usar as mais recentes)
            for year in range(1990, 2025):
                season_name = f"{year}-{str(year + 1)[-2:]}"
                seasons.append({
                    "url": f"https://fbref.com/en/comps/11/{season_name}/schedule/{season_name}-Serie-A-Scores-and-Fixtures",
                    "season": season_name,
                    "year": str(year)
                })
                
        elif "Bundesliga" in competition_url:
            # Bundesliga: 1963-2024 (61 temporadas)
            for year in range(1963, 2025):
                season_name = f"{year}-{str(year + 1)[-2:]}"
                seasons.append({
                    "url": f"https://fbref.com/en/comps/20/{season_name}/schedule/{season_name}-Bundesliga-Scores-and-Fixtures",
                    "season": season_name,
                    "year": str(year)
                })
                
        elif "Ligue-1" in competition_url:
            # Ligue 1: 1932-2024 (92 temporadas, mas vamos usar as mais recentes)
            for year in range(1990, 2025):
                season_name = f"{year}-{str(year + 1)[-2:]}"
                seasons.append({
                    "url": f"https://fbref.com/en/comps/13/{season_name}/schedule/{season_name}-Ligue-1-Scores-and-Fixtures",
                    "season": season_name,
                    "year": str(year)
                })
                
        elif "Champions-League" in competition_url:
            # Champions League: 1955-2024 (69 temporadas)
            for year in range(1955, 2025):
                season_name = f"{year}-{str(year + 1)[-2:]}"
                seasons.append({
                    "url": f"https://fbref.com/en/comps/8/{season_name}/schedule/{season_name}-UEFA-Champions-League-Scores-and-Fixtures",
                    "season": season_name,
                    "year": str(year)
                })
                
        elif "Europa-League" in competition_url:
            # Europa League: 1971-2024 (53 temporadas)
            for year in range(1971, 2025):
                season_name = f"{year}-{str(year + 1)[-2:]}"
                seasons.append({
                    "url": f"https://fbref.com/en/comps/19/{season_name}/schedule/{season_name}-UEFA-Europa-League-Scores-and-Fixtures",
                    "season": season_name,
                    "year": str(year)
                })
                
        elif "World-Cup" in competition_url:
            # World Cup: 1930-2022 (22 edições)
            world_cup_years = [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022]
            for year in world_cup_years:
                seasons.append({
                    "url": f"https://fbref.com/en/comps/1/{year}/schedule/{year}-FIFA-World-Cup-Scores-and-Fixtures",
                    "season": str(year),
                    "year": str(year)
                })
                
        else:
            # Fallback genérico para outras competições
            for year in range(2010, 2025):
                season_name = f"{year}-{str(year + 1)[-2:]}"
                seasons.append({
                    "url": f"https://fbref.com/en/comps/999/{season_name}/schedule/{season_name}-Competition-Scores-and-Fixtures",
                    "season": season_name,
                    "year": str(year)
                })
        
        logger.info(f"Geradas {len(seasons)} temporadas de fallback para: {competition_url}")
        return seasons
    
    def is_site_accessible(self) -> bool:
        """Verifica se o site FBRef está acessível com timeout rígido e fallback seguro."""
        import threading
        import time
        
        logger.info("🔍 Verificação rápida de acessibilidade do FBRef...")
        
        # Resultado compartilhado entre threads
        result = {'accessible': False, 'completed': False}
        
        def check_connection():
            """Função para verificar conectividade em thread separada."""
            try:
                import requests
                # Configuração mínima e rápida
                response = requests.get(
                    "https://fbref.com", 
                    timeout=3,  # Timeout muito baixo
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                if response.status_code == 200:
                    result['accessible'] = True
                    logger.info("✅ FBRef acessível - coleta online habilitada")
                else:
                    logger.info(f"⚠️ FBRef status {response.status_code} - usando fallback")
            except Exception as e:
                logger.info(f"🔄 FBRef inacessível ({type(e).__name__}) - usando fallback")
            finally:
                result['completed'] = True
        
        # Executar verificação em thread com timeout rígido
        thread = threading.Thread(target=check_connection, daemon=True)
        thread.start()
        
        # Aguardar no máximo 5 segundos
        thread.join(timeout=5.0)
        
        if not result['completed']:
            logger.warning("⏰ Verificação de conectividade demorou demais - usando fallback")
            return False
        
        if result['accessible']:
            logger.info("🌐 Modo online ativado - tentará coleta do FBRef")
            return True
        else:
            logger.info("📦 Modo fallback ativado - usando dados locais")
            return False

def create_fallback_system(project_root: str) -> FBRefFallbackSystem:
    """Factory function para criar o sistema de fallback."""
    system = FBRefFallbackSystem(project_root)
    system.save_fallback_data()  # Salva dados iniciais
    return system
