"""
ROUTERS DA API FASTAPI
======================

Pacote contendo todos os routers organizados por domínio.
Cada router implementa endpoints específicos com validação e documentação.

Routers disponíveis:
- competitions: Endpoints para competições esportivas
- clubs: Endpoints para clubes de futebol  
- players: Endpoints para jogadores
- matches: Endpoints para partidas
- social: Endpoints para redes sociais
- news: Endpoints para notícias
- analise: Endpoints para análise de dados
- health: Endpoints de health check e monitoramento

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

from . import competitions, clubs, players, health, social, news, matches, analise

__all__ = [
    "competitions", 
    "clubs", 
    "players", 
    "health", 
    "social", 
    "news", 
    "matches", 
    "analise"
]
