"""
Módulo para análise de sentimento de notícias e posts de redes sociais.

Este módulo fornece funcionalidades para analisar o sentimento de textos,
como notícias e posts de redes sociais, atribuindo pontuações de sentimento
e classificações de polaridade.
"""

import re
import logging
from typing import Dict, Tuple, Optional, List, Any
from datetime import datetime

# Configuração de logging
logger = logging.getLogger(__name__)

# Dicionário de palavras positivas e negativas em português
# Este é um exemplo básico - em produção, considere usar um léxico mais abrangente
# ou um modelo de machine learning treinado
SENTIMENT_LEXICON = {
    # Palavras positivas
    'bom': 1.0, 'bem': 1.0, 'ótimo': 1.5, 'excelente': 1.8, 'maravilhoso': 1.7,
    'incrível': 1.6, 'fantástico': 1.7, 'espetacular': 1.7, 'perfeito': 1.8,
    'vitoria': 1.5, 'vencer': 1.4, 'ganhar': 1.3, 'gol': 0.8, 'golaço': 1.5,
    'gênio': 1.4, 'melhor': 1.3, 'melhorar': 1.2, 'ótima': 1.5, 'ótimo': 1.5,
    'ótimos': 1.5, 'ótimo jogo': 1.7, 'jogão': 1.4, 'show': 1.3,
    
    # Palavras negativas
    'ruim': -1.0, 'mal': -1.0, 'péssimo': -1.5, 'horrível': -1.7, 'terrível': -1.8,
    'fracasso': -1.6, 'derrota': -1.5, 'perder': -1.4, 'perdeu': -1.4, 'perdido': -1.3,
    'erro': -1.2, 'falha': -1.3, 'fracassar': -1.6, 'fracassado': -1.5, 'péssimo jogo': -1.7,
    'desastre': -1.8, 'catastrófico': -1.9, 'decepcionante': -1.6, 'decepcionou': -1.5,
    'péssima atuação': -1.7, 'jogo horrível': -1.8, 'vergonhoso': -1.9
}

# Palavras de intensificação que modificam o sentimento
INTENSIFIERS = {
    'muito': 1.5, 'extremamente': 1.8, 'totalmente': 1.6, 'completamente': 1.6,
    'realmente': 1.3, 'tão': 1.4, 'tanto': 1.3, 'demais': 1.4,
    'pouco': 0.5, 'levemente': 0.6, 'um pouco': 0.7, 'meio': 0.7
}

# Palavras de negação que invertem o sentimento
NEGATIONS = {'não', 'nem', 'nunca', 'jamais', 'tampouco', 'nenhum', 'nada'}

def limpar_texto(texto: str) -> str:
    """
    Limpa e padroniza o texto para análise.
    
    Args:
        texto: Texto a ser limpo
        
    Returns:
        Texto limpo e padronizado
    """
    if not texto:
        return ""
    
    # Converte para minúsculas
    texto = texto.lower()
    
    # Remove URLs
    texto = re.sub(r'https?://\S+|www\.\S+', '', texto)
    
    # Remove menções a usuários (@) e hashtags (#)
    texto = re.sub(r'(@\w+|#\w+)', '', texto)
    
    # Remove caracteres especiais, mas mantém acentos
    texto = re.sub(r'[^\w\sáàâãäéèêëíìîïóòôõöúùûüçñ]', ' ', texto)
    
    # Remove múltiplos espaços em branco
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

def analisar_sentimento_texto(texto: str, titulo: Optional[str] = None) -> Dict[str, Any]:
    """
    Analisa o sentimento de um texto com base em um léxico de palavras.
    
    Args:
        texto: Texto a ser analisado
        titulo: Título do texto (opcional, usado para dar mais peso ao título)
        
    Returns:
        Dicionário com os resultados da análise de sentimento
    """
    if not texto and not titulo:
        return {
            'sentimento_geral': 0.0,
            'confianca': 0.0,
            'polaridade': 'neutro',
            'palavras_chave': [],
            'topicos': [],
            'modelo': 'lexico_basico_v1',
            'analisado_em': datetime.now().isoformat()
        }
    
    # Limpa os textos
    texto_limpo = limpar_texto(texto) if texto else ""
    titulo_limpo = limpar_texto(titulo) if titulo else ""
    
    # Combina título e texto, dando mais peso ao título
    palavras = []
    if titulo_limpo:
        palavras.extend(titulo_limpo.split() * 2)  # Dá mais peso ao título
    if texto_limpo:
        palavras.extend(texto_limpo.split())
    
    if not palavras:
        return {
            'sentimento_geral': 0.0,
            'confianca': 0.0,
            'polaridade': 'neutro',
            'palavras_chave': [],
            'topicos': [],
            'modelo': 'lexico_basico_v1',
            'analisado_em': datetime.now().isoformat()
        }
    
    # Análise de sentimento
    sentimento_total = 0.0
    palavras_com_sentimento = 0
    palavras_chave = []
    
    # Palavras comuns que não são úteis como palavras-chave
    STOP_WORDS = {
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
        'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'sem', 'sob', 'sobre',
        'que', 'e', 'ou', 'se', 'mas', 'como', 'porque', 'pois', 'quando', 'enquanto',
        'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas', 'aquele',
        'aquela', 'aqueles', 'aquelas', 'meu', 'minha', 'meus', 'minhas', 'teu', 'tua',
        'teus', 'tuas', 'seu', 'sua', 'seus', 'suas', 'nosso', 'nossa', 'nossos', 'nossas',
        'deles', 'delas', 'ser', 'estar', 'ter', 'haver', 'fazer', 'poder', 'dizer', 'ir',
        'ver', 'dar', 'saber', 'querer', 'ficar', 'dever', 'passar', 'levar', 'deixar',
        'encontrar', 'chegar', 'partir', 'pôr', 'parecer', 'viver', 'sentir', 'tornar',
        'olhar', 'esperar', 'ficar', 'achar', 'entrar', 'trabalhar', 'falar', 'pensar',
        'sair', 'voltar', 'pegar', 'começar', 'mostrar', 'ouvir', 'tentar', 'tratar',
        'olhar', 'acreditar', 'segurar', 'perguntar', 'tocar', 'mudar', 'acabar', 'lembrar',
        'aparecer', 'esquecer', 'resultado', 'jogo', 'time', 'clube', 'jogador', 'técnico',
        'partida', 'campeonato', 'brasileirão', 'libertadores', 'copa', 'futebol', 'bola'
    }
    
    # Extrai palavras-chave (substantivos e adjetivos relevantes)
    palavras_chave = [
        palavra for palavra in palavras 
        if len(palavra) > 3 and palavra not in STOP_WORDS
    ]
    
    # Conta a frequência das palavras-chave para identificar tópicos
    from collections import Counter
    contador = Counter(palavras_chave)
    topicos = [palavra for palavra, _ in contador.most_common(5)]
    
    # Processa o texto para análise de sentimento
    i = 0
    n = len(palavras)
    
    while i < n:
        palavra = palavras[i]
        sentimento = 0.0
        intensificador = 1.0
        negacao = 1.0
        
        # Verifica se a palavra atual está no léxico de sentimento
        if palavra in SENTIMENT_LEXICON:
            sentimento = SENTIMENT_LEXICON[palavra]
            
            # Verifica se há um intensificador antes da palavra
            if i > 0 and palavras[i-1] in INTENSIFIERS:
                intensificador = INTENSIFIERS[palavras[i-1]]
            
            # Verifica se há uma negação antes da palavra (até 3 palavras antes)
            for j in range(max(0, i-3), i):
                if j < len(palavras) and palavras[j] in NEGATIONS:
                    negacao = -1.0
                    break
            
            sentimento_total += sentimento * intensificador * negacao
            palavras_com_sentimento += 1
        
        i += 1
    
    # Calcula a pontuação média de sentimento
    if palavras_com_sentimento > 0:
        sentimento_medio = sentimento_total / palavras_com_sentimento
        # Normaliza para o intervalo [-1, 1]
        sentimento_medio = max(-1.0, min(1.0, sentimento_medio))
    else:
        sentimento_medio = 0.0
    
    # Calcula a confiança com base na quantidade de palavras com sentimento
    confianca = min(1.0, palavras_com_sentimento / 5.0)  # Máximo de confiança com 5+ palavras
    
    # Determina a polaridade
    if sentimento_medio > 0.2:
        polaridade = 'positivo'
    elif sentimento_medio < -0.2:
        polaridade = 'negativo'
    else:
        polaridade = 'neutro'
    
    return {
        'sentimento_geral': round(sentimento_medio, 4),
        'confianca': round(confianca, 4),
        'polaridade': polaridade,
        'palavras_chave': palavras_chave[:10],  # Limita a 10 palavras-chave
        'topicos': topicos[:5],  # Limita a 5 tópicos
        'modelo': 'lexico_basico_v1',
        'analisado_em': datetime.now().isoformat()
    }

def analisar_noticia(noticia: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analisa o sentimento de uma notícia.
    
    Args:
        noticia: Dicionário contendo os dados da notícia (deve conter 'titulo' e 'conteudo_completo')
        
    Returns:
        Dicionário com os resultados da análise de sentimento
    """
    if not noticia:
        raise ValueError("O dicionário da notícia não pode ser vazio")
    
    titulo = noticia.get('titulo', '')
    conteudo = noticia.get('conteudo_completo', '')
    
    if not titulo and not conteudo:
        raise ValueError("A notícia deve conter pelo menos um título ou conteúdo")
    
    return analisar_sentimento_texto(conteudo, titulo)

def analisar_lote_noticias(noticias: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analisa o sentimento de uma lista de notícias.
    
    Args:
        noticias: Lista de dicionários contendo os dados das notícias
        
    Returns:
        Lista de dicionários com os resultados da análise de sentimento para cada notícia
    """
    if not noticias:
        return []
    
    resultados = []
    for noticia in noticias:
        try:
            resultado = analisar_noticia(noticia)
            # Adiciona o ID da notícia ao resultado, se disponível
            if 'id' in noticia:
                resultado['noticia_id'] = noticia['id']
            resultados.append(resultado)
        except Exception as e:
            logger.error(f"Erro ao analisar notícia: {e}", exc_info=True)
    
    return resultados
