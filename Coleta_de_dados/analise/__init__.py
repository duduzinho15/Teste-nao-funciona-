"""
Módulo de análise de dados para o ApostaPro.
Inclui análise de sentimento, preparação de dados para ML e outras análises.
"""

from .sentimento import AnalisadorSentimento, executar_analise_sentimento

__all__ = [
    'AnalisadorSentimento',
    'executar_analise_sentimento'
]
