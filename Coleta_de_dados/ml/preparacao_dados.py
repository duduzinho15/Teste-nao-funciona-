"""
Módulo de Preparação de Dados para Machine Learning
Responsável por consolidar dados de estatísticas e sentimento em features para treinamento
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from typing import Tuple, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreparadorDadosML:
    def __init__(self, db_path: str = 'Banco_de_dados/aposta.db'):
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """Estabelece conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def _calcular_forma_time(self, partidas: pd.DataFrame, nome_time: str, data_partida: str, 
                            janela_dias: int = 7) -> dict:
        """Calcula a forma atual de um time baseada nos últimos jogos"""
        try:
            data_partida_dt = datetime.strptime(data_partida, '%Y-%m-%d')
            data_limite = data_partida_dt - timedelta(days=janela_dias)
        except:
            # Se não conseguir parsear a data, usar valores padrão
            return {
                'vitorias': 0, 'empates': 0, 'derrotas': 0,
                'gols_marcados': 0, 'gols_sofridos': 0,
                'pontos': 0, 'forma_score': 0.0
            }
        
        # Filtrar jogos recentes do time
        jogos_recentes = partidas[
            ((partidas['time_casa'] == nome_time) | (partidas['time_visitante'] == nome_time)) &
            (partidas['data'] < data_partida) &
            (partidas['data'] >= data_limite.strftime('%Y-%m-%d'))
        ].copy()
        
        if jogos_recentes.empty:
            return {
                'vitorias': 0, 'empates': 0, 'derrotas': 0,
                'gols_marcados': 0, 'gols_sofridos': 0,
                'pontos': 0, 'forma_score': 0.0
            }
        
        # Calcular estatísticas
        vitorias = 0
        empates = 0
        derrotas = 0
        gols_marcados = 0
        gols_sofridos = 0
        
        for _, jogo in jogos_recentes.iterrows():
            try:
                if jogo['time_casa'] == nome_time:
                    if '-' in jogo['placar']:
                        gols_time, gols_adversario = map(int, jogo['placar'].split('-'))
                    else:
                        gols_time, gols_adversario = 0, 0
                else:
                    if '-' in jogo['placar']:
                        gols_adversario, gols_time = map(int, jogo['placar'].split('-'))
                    else:
                        gols_time, gols_adversario = 0, 0
            except:
                gols_time, gols_adversario = 0, 0
            
            gols_marcados += gols_time
            gols_sofridos += gols_adversario
            
            if gols_time > gols_adversario:
                vitorias += 1
            elif gols_time == gols_adversario:
                empates += 1
            else:
                derrotas += 1
        
        pontos = vitorias * 3 + empates
        total_jogos = len(jogos_recentes)
        forma_score = pontos / (total_jogos * 3) if total_jogos > 0 else 0.0
        
        return {
            'vitorias': vitorias,
            'empates': empates,
            'derrotas': derrotas,
            'gols_marcados': gols_marcados,
            'gols_sofridos': gols_sofridos,
            'pontos': pontos,
            'forma_score': forma_score
        }
    
    def _calcular_sentimento_time(self, nome_time: str, data_partida: str, 
                                 janela_dias: int = 7) -> dict:
        """Calcula o sentimento médio de um time baseado em notícias e posts recentes"""
        conn = self._get_connection()
        
        try:
            data_partida_dt = datetime.strptime(data_partida, '%Y-%m-%d')
            data_limite = data_partida_dt - timedelta(days=janela_dias)
        except:
            # Se não conseguir parsear a data, usar valores padrão
            return {
                'sentimento_medio': 0.0,
                'confianca_sentimento': 0.0,
                'total_noticias': 0,
                'total_posts': 0
            }
        
        # Buscar notícias recentes
        query_noticias = """
        SELECT score_sentimento, sentimento
        FROM noticias_clubes 
        WHERE clube_id IN (SELECT id FROM clubes WHERE nome = ?) AND data_publicacao >= ?
        """
        
        noticias = pd.read_sql_query(query_noticias, conn, params=(nome_time, data_limite.strftime('%Y-%m-%d')))
        
        # Buscar posts recentes
        query_posts = """
        SELECT score_sentimento, sentimento
        FROM posts_redes_sociais 
        WHERE clube_id IN (SELECT id FROM clubes WHERE nome = ?) AND data_postagem >= ?
        """
        
        posts = pd.read_sql_query(query_posts, conn, params=(nome_time, data_limite.strftime('%Y-%m-%d')))
        
        conn.close()
        
        # Calcular estatísticas de sentimento
        scores_noticias = noticias['score_sentimento'].dropna()
        scores_posts = posts['score_sentimento'].dropna()
        
        sentimento_medio = 0.0
        confianca = 0.0
        
        if not scores_noticias.empty or not scores_posts.empty:
            todos_scores = pd.concat([scores_noticias, scores_posts])
            sentimento_medio = todos_scores.mean()
            confianca = len(todos_scores) / (janela_dias * 2)  # Normalizado pela janela de tempo
        
        return {
            'sentimento_medio': sentimento_medio,
            'confianca_sentimento': confianca,
            'total_noticias': len(noticias),
            'total_posts': len(posts)
        }
    
    def preparar_dataset_treinamento(self, data_inicio: Optional[datetime] = None, 
                                   data_fim: Optional[datetime] = None) -> pd.DataFrame:
        """
        Prepara o dataset completo para treinamento de modelos ML
        
        Args:
            data_inicio: Data de início para filtrar partidas (padrão: 30 dias atrás)
            data_fim: Data de fim para filtrar partidas (padrão: hoje)
        
        Returns:
            DataFrame com features para treinamento
        """
        if data_inicio is None:
            data_inicio = datetime.now() - timedelta(days=30)
        if data_fim is None:
            data_fim = datetime.now()
        
        logger.info(f"Preparando dataset de treinamento de {data_inicio} até {data_fim}")
        
        conn = self._get_connection()
        
        # Buscar partidas com resultados conhecidos
        query_partidas = """
        SELECT 
            p.id,
            p.data,
            p.time_casa,
            p.time_visitante,
            p.placar,
            tc.nome as nome_time_casa,
            tv.nome as nome_time_visitante
        FROM partidas p
        JOIN clubes tc ON p.time_casa = tc.nome
        JOIN clubes tv ON p.time_visitante = tv.nome
        WHERE p.placar IS NOT NULL
        AND p.placar != ''
        ORDER BY p.id
        LIMIT 100
        """
        
        partidas = pd.read_sql_query(query_partidas, conn)
        conn.close()
        
        if partidas.empty:
            logger.warning("Nenhuma partida encontrada para o período especificado")
            return pd.DataFrame()
        
        logger.info(f"Encontradas {len(partidas)} partidas para análise")
        
        # Preparar features para cada partida
        features_list = []
        
        for _, partida in partidas.iterrows():
            try:
                # Calcular forma dos times
                forma_casa = self._calcular_forma_time(partidas, partida['time_casa'], partida['data'])
                forma_visitante = self._calcular_forma_time(partidas, partida['time_visitante'], partida['data'])
                
                # Calcular sentimento dos times
                sentimento_casa = self._calcular_sentimento_time(partida['time_casa'], partida['data'])
                sentimento_visitante = self._calcular_sentimento_time(partida['time_visitante'], partida['data'])
                
                # Definir target (resultado da partida) - parsear placar do formato "2-1"
                placar = partida['placar']
                try:
                    if '-' in placar:
                        gols_casa, gols_visitante = map(int, placar.split('-'))
                    else:
                        # Se não conseguir parsear, usar valores padrão
                        gols_casa, gols_visitante = 0, 0
                except:
                    gols_casa, gols_visitante = 0, 0
                
                if gols_casa > gols_visitante:
                    resultado = 'casa'
                elif gols_casa < gols_visitante:
                    resultado = 'visitante'
                else:
                    resultado = 'empate'
                
                # Criar features
                features = {
                    'partida_id': partida['id'],
                    'data_partida': partida['data'],
                    
                    # Features do time da casa
                    'casa_forma_score': forma_casa['forma_score'],
                    'casa_vitorias': forma_casa['vitorias'],
                    'casa_empates': forma_casa['empates'],
                    'casa_derrotas': forma_casa['derrotas'],
                    'casa_gols_marcados': forma_casa['gols_marcados'],
                    'casa_gols_sofridos': forma_casa['gols_sofridos'],
                    'casa_sentimento': sentimento_casa['sentimento_medio'],
                    'casa_confianca_sentimento': sentimento_casa['confianca_sentimento'],
                    
                    # Features do time visitante
                    'visitante_forma_score': forma_visitante['forma_score'],
                    'visitante_vitorias': forma_visitante['vitorias'],
                    'visitante_empates': forma_visitante['empates'],
                    'visitante_derrotas': forma_visitante['derrotas'],
                    'visitante_gols_marcados': forma_visitante['gols_marcados'],
                    'visitante_gols_sofridos': forma_visitante['gols_sofridos'],
                    'visitante_sentimento': sentimento_visitante['sentimento_medio'],
                    'visitante_confianca_sentimento': sentimento_visitante['confianca_sentimento'],
                    
                    # Features derivadas
                    'diferenca_forma': forma_casa['forma_score'] - forma_visitante['forma_score'],
                    'diferenca_sentimento': sentimento_casa['sentimento_medio'] - sentimento_visitante['sentimento_medio'],
                    
                    # Target
                    'resultado': resultado,
                    'gols_casa': gols_casa,
                    'gols_visitante': gols_visitante,
                    'total_gols': gols_casa + gols_visitante,
                    'ambas_marcam': 1 if (gols_casa > 0 and gols_visitante > 0) else 0
                }
                
                features_list.append(features)
                
            except Exception as e:
                logger.error(f"Erro ao processar partida {partida['id']}: {e}")
                continue
        
        # Criar DataFrame final
        df_features = pd.DataFrame(features_list)
        
        if not df_features.empty:
            # Limpar dados
            df_features = df_features.dropna()
            
            # Converter tipos
            numeric_columns = df_features.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if col != 'partida_id':
                    df_features[col] = pd.to_numeric(df_features[col], errors='coerce')
            
            # Remover linhas com valores infinitos
            df_features = df_features.replace([np.inf, -np.inf], np.nan).dropna()
            
            logger.info(f"Dataset preparado com sucesso: {len(df_features)} registros, {len(df_features.columns)} features")
        
        return df_features
    
    def salvar_dataset(self, df: pd.DataFrame, filename: str = None) -> str:
        """Salva o dataset preparado em arquivo CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ml_models/data/dataset_treinamento_{timestamp}.csv"
        
        # Criar diretório se não existir
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        df.to_csv(filename, index=False)
        logger.info(f"Dataset salvo em: {filename}")
        
        return filename

def main():
    """Função principal para demonstração"""
    preparador = PreparadorDadosML()
    
    print("🔄 Preparando dataset de treinamento...")
    df = preparador.preparar_dataset_treinamento()
    
    if not df.empty:
        print(f"✅ Dataset preparado com sucesso!")
        print(f"📊 Registros: {len(df)}")
        print(f"🔢 Features: {len(df.columns)}")
        print(f"🎯 Target 'resultado' distribuído:")
        print(df['resultado'].value_counts())
        
        # Salvar dataset
        filename = preparador.salvar_dataset(df)
        print(f"💾 Dataset salvo em: {filename}")
        
        # Mostrar primeiras linhas
        print("\n📋 Primeiras linhas do dataset:")
        print(df.head())
        
    else:
        print("❌ Não foi possível preparar o dataset")

if __name__ == "__main__":
    main()
