"""
Módulo de Machine Learning do ApostaPro
Responsável por preparação de dados, treinamento de modelos e geração de recomendações
"""

from .preparacao_dados import PreparadorDadosML
from .treinamento import TreinadorModeloML
from .gerar_recomendacoes import GeradorRecomendacoes

__all__ = [
    'PreparadorDadosML',
    'TreinadorModeloML', 
    'GeradorRecomendacoes'
]

