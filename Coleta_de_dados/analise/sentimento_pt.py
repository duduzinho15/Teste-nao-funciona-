#!/usr/bin/env python3
"""
Script de Análise de Sentimento para Português Brasileiro
========================================================

Este script analisa o sentimento de notícias e posts de redes sociais
usando um léxico personalizado para português brasileiro.

Autor: Sistema de Análise de Sentimento ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

import sqlite3
import os
import re
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_path():
    """Obtém o caminho para o banco de dados."""
    possible_paths = [
        "Banco_de_dados/aposta.db",
        "Coleta_de_dados/database/football_data.db",
        "aposta.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

class AnalisadorSentimentoPT:
    """Analisador de sentimento para português brasileiro."""
    
    def __init__(self):
        """Inicializa o analisador com léxicos de sentimento."""
        self.palavras_positivas = self._carregar_palavras_positivas()
        self.palavras_negativas = self._carregar_palavras_negativas()
        self.palavras_intensificadoras = self._carregar_intensificadores()
        self.palavras_negacao = self._carregar_negacoes()
        
        logger.info(f"Analisador de sentimento inicializado com {len(self.palavras_positivas)} palavras positivas e {len(self.palavras_negativas)} negativas")
    
    def _carregar_palavras_positivas(self):
        """Carrega léxico de palavras positivas relacionadas ao futebol."""
        return {
            # Vitórias e sucessos
            'vitória', 'vitórias', 'vencer', 'venceu', 'ganhar', 'ganhou', 'triunfo', 'sucesso',
            'campeão', 'campeonato', 'título', 'conquista', 'glória', 'festa', 'celebração',
            
            # Performance positiva
            'excelente', 'brilhante', 'espetacular', 'fantástico', 'incrível', 'maravilhoso',
            'extraordinário', 'excepcional', 'soberbo', 'magnífico', 'perfeito', 'impecável',
            
            # Habilidades
            'talentoso', 'habilidoso', 'técnico', 'inteligente', 'criativo', 'genial',
            'mágico', 'artista', 'craque', 'ídolo', 'lenda', 'fenômeno',
            
            # Emoções positivas
            'feliz', 'alegre', 'contente', 'satisfeito', 'orgulhoso', 'empolgado',
            'animado', 'entusiasmado', 'motivado', 'confiante', 'determinado',
            
            # Futebol específico
            'gol', 'gols', 'assistência', 'finalização', 'drible', 'passe', 'defesa',
            'ataque', 'contra-ataque', 'jogada', 'lances', 'momentos',
            
            # Adjetivos positivos
            'bom', 'ótimo', 'grande', 'forte', 'rápido', 'ágil', 'resistente',
            'competitivo', 'profissional', 'dedicado', 'comprometido', 'focado'
        }
    
    def _carregar_palavras_negativas(self):
        """Carrega léxico de palavras negativas relacionadas ao futebol."""
        return {
            # Derrotas e fracassos
            'derrota', 'derrotas', 'perder', 'perdeu', 'falhar', 'falhou', 'fracasso',
            'desastre', 'catástrofe', 'tragédia', 'humilhação', 'vexame', 'fiasco',
            
            # Performance negativa
            'péssimo', 'terrível', 'horrível', 'ruim', 'fraco', 'medíocre',
            'decepcionante', 'frustrante', 'desanimador', 'desolador', 'lamentável',
            
            # Problemas e dificuldades
            'problema', 'problemas', 'dificuldade', 'obstáculo', 'barreira', 'limitação',
            'deficiência', 'falha', 'erro', 'engano', 'deslize', 'vacilo',
            
            # Emoções negativas
            'triste', 'decepcionado', 'frustrado', 'irritado', 'nervoso', 'ansioso',
            'preocupado', 'desanimado', 'desmotivado', 'desconfiado', 'temeroso',
            
            # Futebol específico negativo
            'falta', 'cartão', 'expulsão', 'lesão', 'contusão', 'suspensão',
            'derrota', 'empate', 'eliminação', 'rebaixamento', 'crise',
            
            # Adjetivos negativos
            'mau', 'fraco', 'lento', 'preguiçoso', 'irresponsável', 'descomprometido',
            'desfocado', 'desorganizado', 'confuso', 'perdido', 'desorientado'
        }
    
    def _carregar_intensificadores(self):
        """Carrega palavras que intensificam o sentimento."""
        return {
            'muito', 'extremamente', 'absolutamente', 'completamente', 'totalmente',
            'incrivelmente', 'extraordinariamente', 'excepcionalmente', 'extremamente',
            'demais', 'demasiadamente', 'excessivamente', 'super', 'mega', 'ultra'
        }
    
    def _carregar_negacoes(self):
        """Carrega palavras de negação."""
        return {
            'não', 'nem', 'jamais', 'nunca', 'nenhum', 'nada', 'ninguém',
            'impossível', 'inviável', 'irrealizável', 'inconcebível'
        }
    
    def analisar_texto(self, texto):
        """
        Analisa o sentimento de um texto.
        
        Args:
            texto: Texto a ser analisado
            
        Returns:
            tuple: (sentimento, score_sentimento, confianca)
        """
        if not texto or not isinstance(texto, str):
            return 'neutro', 0.0, 0.0
        
        # Normaliza o texto
        texto_normalizado = self._normalizar_texto(texto)
        palavras = texto_normalizado.split()
        
        # Conta palavras positivas e negativas
        palavras_positivas_encontradas = []
        palavras_negativas_encontradas = []
        
        score_positivo = 0
        score_negativo = 0
        
        for i, palavra in enumerate(palavras):
            palavra_lower = palavra.lower()
            
            # Verifica se é uma palavra positiva
            if palavra_lower in self.palavras_positivas:
                intensidade = self._calcular_intensidade(palavras, i)
                score_positivo += intensidade
                palavras_positivas_encontradas.append(palavra)
            
            # Verifica se é uma palavra negativa
            elif palavra_lower in self.palavras_negativas:
                intensidade = self._calcular_intensidade(palavras, i)
                score_negativo += intensidade
                palavras_negativas_encontradas.append(palavra)
        
        # Calcula score final
        score_final = score_positivo - score_negativo
        
        # Classifica o sentimento
        sentimento = self._classificar_sentimento(score_final)
        
        # Calcula confiança baseada na quantidade de palavras encontradas
        total_palavras_sentimento = len(palavras_positivas_encontradas) + len(palavras_negativas_encontradas)
        confianca = min(1.0, total_palavras_sentimento / 10)  # Máximo 100% de confiança
        
        return sentimento, score_final, confianca
    
    def _normalizar_texto(self, texto):
        """Normaliza o texto para análise."""
        # Remove caracteres especiais e emojis
        texto = re.sub(r'[^\w\s]', ' ', texto)
        # Remove múltiplos espaços
        texto = re.sub(r'\s+', ' ', texto)
        # Remove espaços no início e fim
        texto = texto.strip()
        return texto
    
    def _calcular_intensidade(self, palavras, indice):
        """Calcula a intensidade de uma palavra baseada no contexto."""
        intensidade = 1.0
        
        # Verifica intensificadores anteriores
        if indice > 0:
            palavra_anterior = palavras[indice - 1].lower()
            if palavra_anterior in self.palavras_intensificadoras:
                intensidade *= 2.0
        
        # Verifica negações
        if indice > 0:
            palavra_anterior = palavras[indice - 1].lower()
            if palavra_anterior in self.palavras_negacao:
                intensidade *= -1.0
        
        return intensidade
    
    def _classificar_sentimento(self, score):
        """Classifica o sentimento baseado no score."""
        if score > 2:
            return 'muito_positivo'
        elif score > 0:
            return 'positivo'
        elif score < -2:
            return 'muito_negativo'
        elif score < 0:
            return 'negativo'
        else:
            return 'neutro'

def analisar_sentimento_textos():
    """
    Busca por notícias e posts sem análise de sentimento, calcula o sentimento
    usando o analisador personalizado para português e atualiza os registros no banco de dados.
    """
    db_path = get_db_path()
    
    if not db_path:
        logger.error("Nenhum banco de dados encontrado!")
        return False
    
    print("🚀 Iniciando análise de sentimento de textos pendentes...")
    print(f"🔍 Conectando ao banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Inicializar analisador
        analisador = AnalisadorSentimentoPT()
        
        # Buscar notícias sem análise de sentimento
        cursor.execute("""
            SELECT id, titulo, resumo, conteudo_completo 
            FROM noticias_clubes 
            WHERE sentimento IS NULL OR score_sentimento IS NULL
        """)
        noticias_pendentes = cursor.fetchall()
        
        # Buscar posts sem análise de sentimento
        cursor.execute("""
            SELECT id, conteudo 
            FROM posts_redes_sociais 
            WHERE sentimento IS NULL OR score_sentimento IS NULL
        """)
        posts_pendentes = cursor.fetchall()
        
        total_itens = len(noticias_pendentes) + len(posts_pendentes)
        
        if total_itens == 0:
            print("✅ Nenhum item novo para analisar.")
            return True
        
        print(f"📊 Encontrados {len(noticias_pendentes)} notícias e {len(posts_pendentes)} posts para análise")
        
        # Processar notícias
        noticias_processadas = 0
        for noticia_id, titulo, resumo, conteudo_completo in noticias_pendentes:
            try:
                # Combinar título, resumo e conteúdo para análise
                texto_completo = f"{titulo or ''} {resumo or ''} {conteudo_completo or ''}".strip()
                
                if not texto_completo:
                    continue
                
                # Analisar sentimento
                sentimento, score, confianca = analisador.analisar_texto(texto_completo)
                
                # Atualizar banco de dados
                cursor.execute("""
                    UPDATE noticias_clubes 
                    SET sentimento = ?, score_sentimento = ?, 
                        sentimento_geral = ?, confianca_sentimento = ?,
                        polaridade = ?, analisado_em = ?, modelo_analise = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (sentimento, score, score, confianca, sentimento, datetime.now(), 'AnalisadorSentimentoPT', noticia_id))
                
                noticias_processadas += 1
                
                if noticias_processadas % 10 == 0:
                    print(f"📰 Processadas {noticias_processadas} notícias...")
                    
            except Exception as e:
                logger.error(f"Erro ao processar notícia {noticia_id}: {e}")
                continue
        
        # Processar posts
        posts_processados = 0
        for post_id, conteudo in posts_pendentes:
            try:
                if not conteudo or not conteudo.strip():
                    continue
                
                # Analisar sentimento
                sentimento, score, confianca = analisador.analisar_texto(conteudo)
                
                # Atualizar banco de dados
                cursor.execute("""
                    UPDATE posts_redes_sociais 
                    SET sentimento = ?, score_sentimento = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (sentimento, score, post_id))
                
                posts_processados += 1
                
                if posts_processados % 10 == 0:
                    print(f"📱 Processados {posts_processados} posts...")
                    
            except Exception as e:
                logger.error(f"Erro ao processar post {post_id}: {e}")
                continue
        
        # Commit das alterações
        conn.commit()
        
        print(f"\n✅ Análise de sentimento concluída!")
        print(f"📊 Resumo:")
        print(f"   - Notícias processadas: {noticias_processadas}")
        print(f"   - Posts processados: {posts_processados}")
        print(f"   - Total: {noticias_processadas + posts_processados}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante análise de sentimento: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def obter_estatisticas_sentimento():
    """
    Obtém estatísticas sobre a análise de sentimento realizada.
    
    Returns:
        dict: Estatísticas de sentimento
    """
    db_path = get_db_path()
    
    if not db_path:
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Estatísticas de notícias
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN sentimento = 'positivo' THEN 1 END) as positivas,
                COUNT(CASE WHEN sentimento = 'negativo' THEN 1 END) as negativas,
                COUNT(CASE WHEN sentimento = 'neutro' THEN 1 END) as neutras,
                AVG(score_sentimento) as score_medio
            FROM noticias_clubes 
            WHERE sentimento IS NOT NULL
        """)
        stats_noticias = cursor.fetchall()
        
        # Estatísticas de posts
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN sentimento = 'positivo' THEN 1 END) as positivos,
                COUNT(CASE WHEN sentimento = 'negativo' THEN 1 END) as negativos,
                COUNT(CASE WHEN sentimento = 'neutro' THEN 1 END) as neutros,
                AVG(score_sentimento) as score_medio
            FROM posts_redes_sociais 
            WHERE sentimento IS NOT NULL
        """)
        stats_posts = cursor.fetchall()
        
        # Sentimento por clube (top 5)
        cursor.execute("""
            SELECT 
                c.nome as clube,
                COUNT(n.id) as total_noticias,
                AVG(n.score_sentimento) as score_medio,
                COUNT(CASE WHEN n.sentimento = 'positivo' THEN 1 END) as positivas,
                COUNT(CASE WHEN n.sentimento = 'negativo' THEN 1 END) as negativas
            FROM noticias_clubes n
            JOIN clubes c ON n.clube_id = c.id
            WHERE n.sentimento IS NOT NULL
            GROUP BY c.id, c.nome
            ORDER BY total_noticias DESC
            LIMIT 5
        """)
        top_clubes = cursor.fetchall()
        
        return {
            'noticias': {
                'total': stats_noticias[0] or 0,
                'positivas': stats_noticias[1] or 0,
                'negativas': stats_noticias[2] or 0,
                'neutras': stats_noticias[3] or 0,
                'score_medio': stats_noticias[4] or 0.0
            },
            'posts': {
                'total': stats_posts[0] or 0,
                'positivos': stats_posts[1] or 0,
                'negativos': stats_posts[2] or 0,
                'neutros': stats_posts[3] or 0,
                'score_medio': stats_posts[4] or 0.0
            },
            'top_clubes': [
                {
                    'nome': clube[0],
                    'total_noticias': clube[1],
                    'score_medio': clube[2] or 0.0,
                    'positivas': clube[3],
                    'negativas': clube[4]
                }
                for clube in top_clubes
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return None
    
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Função principal."""
    print("🧠 Sistema de Análise de Sentimento para Português Brasileiro")
    print("=" * 60)
    
    # Executar análise de sentimento
    success = analisar_sentimento_textos()
    
    if success:
        print("\n📊 Obtendo estatísticas...")
        stats = obter_estatisticas_sentimento()
        
        if stats:
            print("\n📈 Estatísticas de Sentimento:")
            print(f"📰 Notícias:")
            print(f"   - Total: {stats['noticias']['total']}")
            print(f"   - Positivas: {stats['noticias']['positivas']}")
            print(f"   - Negativas: {stats['noticias']['negativas']}")
            print(f"   - Neutras: {stats['noticias']['neutras']}")
            print(f"   - Score médio: {stats['noticias']['score_medio']:.3f}")
            
            print(f"\n📱 Posts:")
            print(f"   - Total: {stats['posts']['total']}")
            print(f"   - Positivos: {stats['posts']['positivos']}")
            print(f"   - Negativos: {stats['posts']['negativos']}")
            print(f"   - Neutros: {stats['posts']['neutros']}")
            print(f"   - Score médio: {stats['posts']['score_medio']:.3f}")
            
            if stats['top_clubes']:
                print(f"\n🏆 Top 5 Clubes por Notícias:")
                for i, clube in enumerate(stats['top_clubes'], 1):
                    print(f"   {i}. {clube['nome']}: {clube['total_noticias']} notícias (score: {clube['score_medio']:.3f})")
        
        print("\n🎉 Análise de sentimento concluída com sucesso!")
    else:
        print("\n❌ Falha na análise de sentimento.")
    
    return success

if __name__ == '__main__':
    main()
