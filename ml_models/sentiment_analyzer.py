#!/usr/bin/env python3
"""
Sistema avançado de análise de sentimento para notícias e posts esportivos
"""

import logging
from typing import Dict, List, Tuple, Optional, Union
import numpy as np
from datetime import datetime, timedelta
import re
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result

# Configurar logging
logger = logging.getLogger(__name__)

# Download recursos NLTK necessários
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class SentimentAnalyzer:
    """Analisador de sentimento avançado para conteúdo esportivo"""
    
    def __init__(self):
        self.config = get_ml_config()
        self.lemmatizer = WordNetLemmatizer()
        
        # Palavras específicas do futebol com polaridade
        self.football_sentiment_words = {
            'gol': 0.8, 'vitória': 0.9, 'derrota': -0.9, 'empate': 0.0,
            'campeão': 1.0, 'rebaixamento': -1.0, 'classificação': 0.3,
            'lesão': -0.7, 'suspensão': -0.6, 'cartão vermelho': -0.8,
            'cartão amarelo': -0.4, 'pênalti': 0.5, 'falta': -0.3,
            'assistência': 0.7, 'defesa': 0.4, 'ataque': 0.6,
            'técnico': 0.2, 'treinador': 0.2, 'jogador': 0.1,
            'estádio': 0.3, 'torcida': 0.5, 'rival': -0.2,
            'transferência': 0.4, 'contrato': 0.3, 'renovação': 0.6
        }
        
        # Expressões idiomáticas do futebol
        self.football_idioms = {
            'jogo do século': 0.9,
            'clássico': 0.7,
            'derby': 0.8,
            'final': 0.9,
            'semifinal': 0.8,
            'quartas de final': 0.7,
            'oitavas de final': 0.6,
            'grupo da morte': -0.3,
            'fase de grupos': 0.4,
            'playoff': 0.6,
            'promoção': 0.8,
            'rebaixamento': -0.8
        }
    
    def preprocess_text(self, text: str) -> str:
        """Pré-processa o texto para análise"""
        if not text:
            return ""
        
        # Converter para minúsculas
        text = text.lower()
        
        # Remover URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remover hashtags mas manter o texto
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Remover menções
        text = re.sub(r'@(\w+)', '', text)
        
        # Remover caracteres especiais mas manter acentos
        text = re.sub(r'[^\w\sáàâãéèêíìîóòôõúùûç]', ' ', text)
        
        # Remover espaços extras
        text = ' '.join(text.split())
        
        return text
    
    def extract_football_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave relacionadas ao futebol"""
        football_keywords = []
        text_lower = text.lower()
        
        for keyword in self.football_sentiment_words.keys():
            if keyword in text_lower:
                football_keywords.append(keyword)
        
        for idiom in self.football_idioms.keys():
            if idiom in text_lower:
                football_keywords.append(idiom)
        
        return football_keywords
    
    @timed_cache_result(ttl_hours=12)
    def analyze_sentiment_textblob(self, text: str) -> Dict[str, Union[float, str, List[str]]]:
        """Análise de sentimento usando TextBlob"""
        try:
            preprocessed_text = self.preprocess_text(text)
            if not preprocessed_text:
                return {
                    'sentiment_score': 0.0,
                    'sentiment_label': 'neutral',
                    'confidence': 0.0,
                    'football_keywords': [],
                    'analysis_method': 'textblob'
                }
            
            # Análise TextBlob
            blob = TextBlob(preprocessed_text)
            sentiment_score = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determinar label baseado no score
            if sentiment_score > 0.1:
                sentiment_label = 'positive'
            elif sentiment_score < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            # Extrair palavras-chave do futebol
            football_keywords = self.extract_football_keywords(text)
            
            # Calcular confiança baseada na subjetividade
            confidence = min(1.0, max(0.0, 1.0 - subjectivity))
            
            return {
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_label': sentiment_label,
                'confidence': round(confidence, 3),
                'subjectivity': round(subjectivity, 3),
                'football_keywords': football_keywords,
                'analysis_method': 'textblob',
                'preprocessed_text': preprocessed_text
            }
            
        except Exception as e:
            logger.error(f"Erro na análise TextBlob: {e}")
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'error',
                'confidence': 0.0,
                'football_keywords': [],
                'analysis_method': 'textblob',
                'error': str(e)
            }
    
    def analyze_sentiment_lexical(self, text: str) -> Dict[str, Union[float, str, List[str]]]:
        """Análise de sentimento baseada em léxico esportivo"""
        try:
            preprocessed_text = self.preprocess_text(text)
            if not preprocessed_text:
                return {
                    'sentiment_score': 0.0,
                    'sentiment_label': 'neutral',
                    'confidence': 0.0,
                    'football_keywords': [],
                    'analysis_method': 'lexical'
                }
            
            words = word_tokenize(preprocessed_text)
            total_score = 0.0
            matched_words = 0
            
            # Calcular score baseado no léxico esportivo
            for word in words:
                word_lemma = self.lemmatizer.lemmatize(word)
                
                # Verificar palavras do futebol
                if word_lemma in self.football_sentiment_words:
                    total_score += self.football_sentiment_words[word_lemma]
                    matched_words += 1
                
                # Verificar expressões idiomáticas
                for idiom, score in self.football_idioms.items():
                    if idiom in preprocessed_text:
                        total_score += score
                        matched_words += 1
            
            # Normalizar score
            if matched_words > 0:
                sentiment_score = total_score / matched_words
                confidence = min(1.0, matched_words / 10.0)  # Mais palavras = mais confiança
            else:
                sentiment_score = 0.0
                confidence = 0.0
            
            # Determinar label
            if sentiment_score > 0.1:
                sentiment_label = 'positive'
            elif sentiment_score < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            football_keywords = self.extract_football_keywords(text)
            
            return {
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_label': sentiment_label,
                'confidence': round(confidence, 3),
                'matched_words': matched_words,
                'football_keywords': football_keywords,
                'analysis_method': 'lexical',
                'preprocessed_text': preprocessed_text
            }
            
        except Exception as e:
            logger.error(f"Erro na análise léxica: {e}")
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'error',
                'confidence': 0.0,
                'football_keywords': [],
                'analysis_method': 'lexical',
                'error': str(e)
            }
    
    @timed_cache_result(ttl_hours=6)
    def analyze_sentiment_hybrid(self, text: str) -> Dict[str, Union[float, str, List[str]]]:
        """Análise híbrida combinando TextBlob e léxico esportivo"""
        try:
            # Análises individuais
            textblob_result = self.analyze_sentiment_textblob(text)
            lexical_result = self.analyze_sentiment_lexical(text)
            
            # Peso para cada método (TextBlob tem mais peso para texto geral)
            textblob_weight = 0.6
            lexical_weight = 0.4
            
            # Score híbrido
            hybrid_score = (
                textblob_result['sentiment_score'] * textblob_weight +
                lexical_result['sentiment_score'] * lexical_weight
            )
            
            # Confiança híbrida
            hybrid_confidence = (
                textblob_result['confidence'] * textblob_weight +
                lexical_result['confidence'] * lexical_weight
            )
            
            # Determinar label final
            if hybrid_score > 0.1:
                sentiment_label = 'positive'
            elif hybrid_score < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            # Combinar palavras-chave únicas
            all_keywords = list(set(
                textblob_result['football_keywords'] + 
                lexical_result['football_keywords']
            ))
            
            return {
                'sentiment_score': round(hybrid_score, 3),
                'sentiment_label': sentiment_label,
                'confidence': round(hybrid_confidence, 3),
                'textblob_score': textblob_result['sentiment_score'],
                'lexical_score': lexical_result['sentiment_score'],
                'football_keywords': all_keywords,
                'analysis_method': 'hybrid',
                'textblob_confidence': textblob_result['confidence'],
                'lexical_confidence': lexical_result['confidence']
            }
            
        except Exception as e:
            logger.error(f"Erro na análise híbrida: {e}")
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'error',
                'confidence': 0.0,
                'football_keywords': [],
                'analysis_method': 'hybrid',
                'error': str(e)
            }
    
    def analyze_batch_sentiments(self, texts: List[str], method: str = 'hybrid') -> List[Dict]:
        """Analisa sentimento de uma lista de textos"""
        results = []
        
        for i, text in enumerate(texts):
            try:
                if method == 'textblob':
                    result = self.analyze_sentiment_textblob(text)
                elif method == 'lexical':
                    result = self.analyze_sentiment_lexical(text)
                else:
                    result = self.analyze_sentiment_hybrid(text)
                
                result['text_index'] = i
                result['original_text'] = text[:100] + '...' if len(text) > 100 else text
                results.append(result)
                
            except Exception as e:
                logger.error(f"Erro ao analisar texto {i}: {e}")
                results.append({
                    'text_index': i,
                    'sentiment_score': 0.0,
                    'sentiment_label': 'error',
                    'confidence': 0.0,
                    'error': str(e),
                    'analysis_method': method
                })
        
        return results
    
    def get_sentiment_summary(self, results: List[Dict]) -> Dict[str, Union[float, int, str]]:
        """Gera um resumo das análises de sentimento"""
        if not results:
            return {}
        
        valid_results = [r for r in results if r['sentiment_label'] != 'error']
        
        if not valid_results:
            return {'error': 'Nenhum resultado válido encontrado'}
        
        # Estatísticas básicas
        total_texts = len(valid_results)
        positive_count = len([r for r in valid_results if r['sentiment_label'] == 'positive'])
        negative_count = len([r for r in valid_results if r['sentiment_label'] == 'negative'])
        neutral_count = len([r for r in valid_results if r['sentiment_label'] == 'neutral'])
        
        # Scores médios
        avg_sentiment = np.mean([r['sentiment_score'] for r in valid_results])
        avg_confidence = np.mean([r['confidence'] for r in valid_results])
        
        # Palavras-chave mais comuns
        all_keywords = []
        for r in valid_results:
            all_keywords.extend(r.get('football_keywords', []))
        
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_texts': total_texts,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_percentage': round((positive_count / total_texts) * 100, 2),
            'negative_percentage': round((negative_count / total_texts) * 100, 2),
            'neutral_percentage': round((neutral_count / total_texts) * 100, 2),
            'average_sentiment_score': round(avg_sentiment, 3),
            'average_confidence': round(avg_confidence, 3),
            'top_football_keywords': top_keywords,
            'analysis_timestamp': datetime.now().isoformat()
        }

# Instância global
sentiment_analyzer = SentimentAnalyzer()

# Funções de conveniência
def analyze_sentiment(text: str, method: str = 'hybrid') -> Dict:
    """Analisa sentimento de um texto"""
    return sentiment_analyzer.analyze_sentiment_hybrid(text)

def analyze_sentiments_batch(texts: List[str], method: str = 'hybrid') -> List[Dict]:
    """Analisa sentimento de uma lista de textos"""
    return sentiment_analyzer.analyze_batch_sentiments(texts, method)

def get_sentiment_summary(results: List[Dict]) -> Dict:
    """Gera resumo das análises de sentimento"""
    return sentiment_analyzer.get_sentiment_summary(results)
