#!/usr/bin/env python3
"""
Módulo de preparação de dados para Machine Learning.
Prepara e engenheira features para treinamento de modelos de previsão de apostas.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreparadorDadosML:
    """Preparador de dados para Machine Learning no contexto de apostas esportivas."""
    
    def __init__(self, db_session: Session):
        """
        Inicializa o preparador de dados.
        
        Args:
            db_session: Sessão do banco de dados
        """
        self.db_session = db_session
        self.features_estatisticas = [
            'gols_marcados', 'gols_sofridos', 'vitorias', 'empates', 'derrotas',
            'pontos', 'jogos', 'gols_marcados_casa', 'gols_sofridos_casa',
            'gols_marcados_fora', 'gols_sofridos_fora', 'vitorias_casa',
            'empates_casa', 'derrotas_casa', 'vitorias_fora', 'empates_fora',
            'derrotas_fora'
        ]
        
        logger.info("🔧 Preparador de dados ML inicializado")
    
    def carregar_dados_partidas(self, data_inicio: Optional[datetime] = None, 
                               data_fim: Optional[datetime] = None) -> pd.DataFrame:
        """
        Carrega dados de partidas do banco de dados.
        
        Args:
            data_inicio: Data de início para filtrar partidas
            data_fim: Data de fim para filtrar partidas
            
        Returns:
            DataFrame com dados das partidas
        """
        try:
            # Query base para partidas
            query = """
                SELECT 
                    p.id,
                    p.data_partida,
                    p.gols_casa,
                    p.gols_visitante,
                    p.estadio,
                    p.arbitro,
                    p.status,
                    c1.nome as clube_casa,
                    c1.id as clube_casa_id,
                    c2.nome as clube_visitante,
                    c2.id as clube_visitante_id,
                    comp.nome as competicao,
                    comp.id as competicao_id
                FROM partidas p
                JOIN clubes c1 ON p.clube_casa_id = c1.id
                JOIN clubes c2 ON p.clube_visitante_id = c2.id
                JOIN competicoes comp ON p.competicao_id = comp.id
                WHERE p.status = 'finalizada'
            """
            
            params = {}
            if data_inicio:
                query += " AND p.data_partida >= :data_inicio"
                params['data_inicio'] = data_inicio
            if data_fim:
                query += " AND p.data_partida <= :data_fim"
                params['data_fim'] = data_fim
            
            query += " ORDER BY p.data_partida DESC"
            
            # Executa query
            result = self.db_session.execute(text(query), params)
            partidas = result.fetchall()
            
            if not partidas:
                logger.warning("⚠️ Nenhuma partida encontrada no período especificado")
                return pd.DataFrame()
            
            # Converte para DataFrame
            df_partidas = pd.DataFrame(partidas)
            
            # Calcula resultado da partida
            df_partidas['resultado'] = df_partidas.apply(
                lambda row: self._calcular_resultado(row['gols_casa'], row['gols_visitante']), 
                axis=1
            )
            
            # Calcula total de gols
            df_partidas['total_gols'] = df_partidas['gols_casa'] + df_partidas['gols_visitante']
            
            # Calcula diferença de gols
            df_partidas['diferenca_gols'] = df_partidas['gols_casa'] - df_partidas['gols_visitante']
            
            logger.info(f"✅ {len(df_partidas)} partidas carregadas")
            return df_partidas
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados de partidas: {e}")
            return pd.DataFrame()
    
    def carregar_estatisticas_clubes(self, data_referencia: Optional[datetime] = None) -> pd.DataFrame:
        """
        Carrega estatísticas dos clubes até uma data de referência.
        
        Args:
            data_referencia: Data de referência para calcular estatísticas
            
        Returns:
            DataFrame com estatísticas dos clubes
        """
        try:
            if not data_referencia:
                data_referencia = datetime.now()
            
            # Query para estatísticas dos clubes
            query = """
                SELECT 
                    c.id as clube_id,
                    c.nome as clube_nome,
                    COALESCE(SUM(CASE WHEN p.clube_casa_id = c.id THEN p.gols_casa ELSE 0 END), 0) as gols_marcados_casa,
                    COALESCE(SUM(CASE WHEN p.clube_casa_id = c.id THEN p.gols_visitante ELSE 0 END), 0) as gols_sofridos_casa,
                    COALESCE(SUM(CASE WHEN p.clube_visitante_id = c.id THEN p.gols_visitante ELSE 0 END), 0) as gols_marcados_fora,
                    COALESCE(SUM(CASE WHEN p.clube_visitante_id = c.id THEN p.gols_casa ELSE 0 END), 0) as gols_sofridos_fora,
                    COALESCE(SUM(CASE WHEN p.clube_casa_id = c.id THEN 
                        CASE WHEN p.gols_casa > p.gols_visitante THEN 1 ELSE 0 END
                    ELSE 0 END), 0) as vitorias_casa,
                    COALESCE(SUM(CASE WHEN p.clube_casa_id = c.id THEN 
                        CASE WHEN p.gols_casa = p.gols_visitante THEN 1 ELSE 0 END
                    ELSE 0 END), 0) as empates_casa,
                    COALESCE(SUM(CASE WHEN p.clube_casa_id = c.id THEN 
                        CASE WHEN p.gols_casa < p.gols_visitante THEN 1 ELSE 0 END
                    ELSE 0 END), 0) as derrotas_casa,
                    COALESCE(SUM(CASE WHEN p.clube_visitante_id = c.id THEN 
                        CASE WHEN p.gols_visitante > p.gols_casa THEN 1 ELSE 0 END
                    ELSE 0 END), 0) as vitorias_fora,
                    COALESCE(SUM(CASE WHEN p.clube_visitante_id = c.id THEN 
                        CASE WHEN p.gols_visitante = p.gols_casa THEN 1 ELSE 0 END
                    ELSE 0 END), 0) as empates_fora,
                    COALESCE(SUM(CASE WHEN p.clube_visitante_id = c.id THEN 
                        CASE WHEN p.gols_visitante < p.gols_casa THEN 1 ELSE 0 END
                    ELSE 0 END), 0) as derrotas_fora
                FROM clubes c
                LEFT JOIN partidas p ON (p.clube_casa_id = c.id OR p.clube_visitante_id = c.id)
                    AND p.status = 'finalizada' 
                    AND p.data_partida < :data_referencia
                GROUP BY c.id, c.nome
            """
            
            result = self.db_session.execute(text(query), {'data_referencia': data_referencia})
            estatisticas = result.fetchall()
            
            if not estatisticas:
                logger.warning("⚠️ Nenhuma estatística de clube encontrada")
                return pd.DataFrame()
            
            # Converte para DataFrame
            df_estatisticas = pd.DataFrame(estatisticas)
            
            # Calcula estatísticas agregadas
            df_estatisticas['gols_marcados'] = df_estatisticas['gols_marcados_casa'] + df_estatisticas['gols_marcados_fora']
            df_estatisticas['gols_sofridos'] = df_estatisticas['gols_sofridos_casa'] + df_estatisticas['gols_sofridos_fora']
            df_estatisticas['vitorias'] = df_estatisticas['vitorias_casa'] + df_estatisticas['vitorias_fora']
            df_estatisticas['empates'] = df_estatisticas['empates_casa'] + df_estatisticas['empates_fora']
            df_estatisticas['derrotas'] = df_estatisticas['derrotas_casa'] + df_estatisticas['derrotas_fora']
            df_estatisticas['jogos'] = df_estatisticas['vitorias'] + df_estatisticas['empates'] + df_estatisticas['derrotas']
            df_estatisticas['pontos'] = df_estatisticas['vitorias'] * 3 + df_estatisticas['empates']
            
            # Calcula médias por jogo
            df_estatisticas['gols_marcados_por_jogo'] = np.where(
                df_estatisticas['jogos'] > 0,
                df_estatisticas['gols_marcados'] / df_estatisticas['jogos'],
                0
            )
            df_estatisticas['gols_sofridos_por_jogo'] = np.where(
                df_estatisticas['jogos'] > 0,
                df_estatisticas['gols_sofridos'] / df_estatisticas['jogos'],
                0
            )
            
            # Calcula saldo de gols
            df_estatisticas['saldo_gols'] = df_estatisticas['gols_marcados'] - df_estatisticas['gols_sofridos']
            
            # Calcula aproveitamento
            df_estatisticas['aproveitamento'] = np.where(
                df_estatisticas['jogos'] > 0,
                (df_estatisticas['pontos'] / (df_estatisticas['jogos'] * 3)) * 100,
                0
            )
            
            logger.info(f"✅ Estatísticas de {len(df_estatisticas)} clubes carregadas")
            return df_estatisticas
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar estatísticas dos clubes: {e}")
            return pd.DataFrame()
    
    def carregar_sentimento_clubes(self, data_referencia: Optional[datetime] = None) -> pd.DataFrame:
        """
        Carrega dados de sentimento dos clubes.
        
        Args:
            data_referencia: Data de referência para filtrar dados
            
        Returns:
            DataFrame com dados de sentimento
        """
        try:
            if not data_referencia:
                data_referencia = datetime.now()
            
            # Query para sentimento de notícias
            query_noticias = """
                SELECT 
                    clube_id,
                    AVG(score_sentimento) as sentimento_medio_noticias,
                    COUNT(*) as total_noticias,
                    MODE() WITHIN GROUP (ORDER BY sentimento) as sentimento_mais_frequente_noticias
                FROM noticias_clubes 
                WHERE data_publicacao >= :data_inicio
                GROUP BY clube_id
            """
            
            # Query para sentimento de posts
            query_posts = """
                SELECT 
                    clube_id,
                    AVG(score_sentimento) as sentimento_medio_posts,
                    COUNT(*) as total_posts,
                    MODE() WITHIN GROUP (ORDER BY sentimento) as sentimento_mais_frequente_posts,
                    AVG(curtidas) as media_curtidas,
                    AVG(comentarios) as media_comentarios,
                    AVG(compartilhamentos) as media_compartilhamentos
                FROM posts_redes_sociais 
                WHERE data_postagem >= :data_inicio
                GROUP BY clube_id
            """
            
            data_inicio = data_referencia - timedelta(days=30)  # Últimos 30 dias
            
            # Executa queries
            result_noticias = self.db_session.execute(text(query_noticias), {'data_inicio': data_inicio})
            result_posts = self.db_session.execute(text(query_posts), {'data_inicio': data_inicio})
            
            noticias = result_noticias.fetchall()
            posts = result_posts.fetchall()
            
            # Converte para DataFrames
            df_noticias = pd.DataFrame(noticias) if noticias else pd.DataFrame()
            df_posts = pd.DataFrame(posts) if posts else pd.DataFrame()
            
            # Combina os dados
            if not df_noticias.empty and not df_posts.empty:
                df_sentimento = pd.merge(df_noticias, df_posts, on='clube_id', how='outer')
            elif not df_noticias.empty:
                df_sentimento = df_noticias
            elif not df_posts.empty:
                df_sentimento = df_posts
            else:
                logger.warning("⚠️ Nenhum dado de sentimento encontrado")
                return pd.DataFrame()
            
            # Preenche valores nulos
            df_sentimento = df_sentimento.fillna(0)
            
            logger.info(f"✅ Dados de sentimento de {len(df_sentimento)} clubes carregados")
            return df_sentimento
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados de sentimento: {e}")
            return pd.DataFrame()
    
    def carregar_historico_confrontos(self, clube_casa_id: int, clube_visitante_id: int, 
                                     data_referencia: Optional[datetime] = None) -> pd.DataFrame:
        """
        Carrega histórico de confrontos entre dois clubes.
        
        Args:
            clube_casa_id: ID do clube da casa
            clube_visitante_id: ID do clube visitante
            data_referencia: Data de referência para filtrar partidas
            
        Returns:
            DataFrame com histórico de confrontos
        """
        try:
            if not data_referencia:
                data_referencia = datetime.now()
            
            # Query para histórico de confrontos
            query = """
                SELECT 
                    p.id,
                    p.data_partida,
                    p.gols_casa,
                    p.gols_visitante,
                    p.clube_casa_id,
                    p.clube_visitante_id,
                    c1.nome as clube_casa,
                    c2.nome as clube_visitante,
                    CASE 
                        WHEN p.clube_casa_id = :clube_casa_id THEN p.gols_casa
                        ELSE p.gols_visitante
                    END as gols_clube_referencia,
                    CASE 
                        WHEN p.clube_casa_id = :clube_casa_id THEN p.gols_visitante
                        ELSE p.gols_casa
                    END as gols_adversario
                FROM partidas p
                JOIN clubes c1 ON p.clube_casa_id = c1.id
                JOIN clubes c2 ON p.clube_visitante_id = c2.id
                WHERE p.status = 'finalizada'
                    AND p.data_partida < :data_referencia
                    AND ((p.clube_casa_id = :clube_casa_id AND p.clube_visitante_id = :clube_visitante_id)
                         OR (p.clube_casa_id = :clube_visitante_id AND p.clube_visitante_id = :clube_casa_id))
                ORDER BY p.data_partida DESC
                LIMIT 10
            """
            
            result = self.db_session.execute(text(query), {
                'clube_casa_id': clube_casa_id,
                'clube_visitante_id': clube_visitante_id,
                'data_referencia': data_referencia
            })
            
            confrontos = result.fetchall()
            
            if not confrontos:
                logger.warning(f"⚠️ Nenhum confronto histórico encontrado entre clubes {clube_casa_id} e {clube_visitante_id}")
                return pd.DataFrame()
            
            # Converte para DataFrame
            df_confrontos = pd.DataFrame(confrontos)
            
            # Calcula estatísticas do histórico
            df_confrontos['resultado_clube_referencia'] = df_confrontos.apply(
                lambda row: self._calcular_resultado_clube_referencia(
                    row['gols_clube_referencia'], row['gols_adversario']
                ), axis=1
            )
            
            # Calcula total de gols
            df_confrontos['total_gols'] = df_confrontos['gols_clube_referencia'] + df_confrontos['gols_adversario']
            
            logger.info(f"✅ {len(df_confrontos)} confrontos históricos carregados")
            return df_confrontos
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar histórico de confrontos: {e}")
            return pd.DataFrame()
    
    def criar_features_partida(self, partida: pd.Series, estatisticas_clubes: pd.DataFrame,
                              sentimento_clubes: pd.DataFrame, historico_confrontos: pd.DataFrame) -> Dict[str, Any]:
        """
        Cria features para uma partida específica.
        
        Args:
            partida: Série com dados da partida
            estatisticas_clubes: DataFrame com estatísticas dos clubes
            sentimento_clubes: DataFrame com dados de sentimento
            historico_confrontos: DataFrame com histórico de confrontos
            
        Returns:
            Dicionário com features da partida
        """
        try:
            clube_casa_id = partida['clube_casa_id']
            clube_visitante_id = partida['clube_visitante_id']
            
            # Features do clube da casa
            stats_casa = estatisticas_clubes[estatisticas_clubes['clube_id'] == clube_casa_id]
            sent_casa = sentimento_clubes[sentimento_clubes['clube_id'] == clube_casa_id]
            
            # Features do clube visitante
            stats_visitante = estatisticas_clubes[estatisticas_clubes['clube_id'] == clube_visitante_id]
            sent_visitante = sentimento_clubes[sentimento_clubes['clube_id'] == clube_visitante_id]
            
            # Features básicas da partida
            features = {
                'partida_id': partida['id'],
                'data_partida': partida['data_partida'],
                'clube_casa_id': clube_casa_id,
                'clube_visitante_id': clube_visitante_id,
                'competicao_id': partida['competicao_id']
            }
            
            # Features do clube da casa
            if not stats_casa.empty:
                casa = stats_casa.iloc[0]
                features.update({
                    'casa_gols_marcados_por_jogo': casa['gols_marcados_por_jogo'],
                    'casa_gols_sofridos_por_jogo': casa['gols_sofridos_por_jogo'],
                    'casa_saldo_gols': casa['saldo_gols'],
                    'casa_aproveitamento': casa['aproveitamento'],
                    'casa_vitorias_casa': casa['vitorias_casa'],
                    'casa_empates_casa': casa['empates_casa'],
                    'casa_derrotas_casa': casa['derrotas_casa'],
                    'casa_pontos': casa['pontos'],
                    'casa_jogos': casa['jogos']
                })
            else:
                # Valores padrão se não houver estatísticas
                features.update({
                    'casa_gols_marcados_por_jogo': 0.0,
                    'casa_gols_sofridos_por_jogo': 0.0,
                    'casa_saldo_gols': 0,
                    'casa_aproveitamento': 0.0,
                    'casa_vitorias_casa': 0,
                    'casa_empates_casa': 0,
                    'casa_derrotas_casa': 0,
                    'casa_pontos': 0,
                    'casa_jogos': 0
                })
            
            # Features do clube visitante
            if not stats_visitante.empty:
                visitante = stats_visitante.iloc[0]
                features.update({
                    'visitante_gols_marcados_por_jogo': visitante['gols_marcados_por_jogo'],
                    'visitante_gols_sofridos_por_jogo': visitante['gols_sofridos_por_jogo'],
                    'visitante_saldo_gols': visitante['saldo_gols'],
                    'visitante_aproveitamento': visitante['aproveitamento'],
                    'visitante_vitorias_fora': visitante['vitorias_fora'],
                    'visitante_empates_fora': visitante['empates_fora'],
                    'visitante_derrotas_fora': visitante['derrotas_fora'],
                    'visitante_pontos': visitante['pontos'],
                    'visitante_jogos': visitante['jogos']
                })
            else:
                # Valores padrão se não houver estatísticas
                features.update({
                    'visitante_gols_marcados_por_jogo': 0.0,
                    'visitante_gols_sofridos_por_jogo': 0.0,
                    'visitante_saldo_gols': 0,
                    'visitante_aproveitamento': 0.0,
                    'visitante_vitorias_fora': 0,
                    'visitante_empates_fora': 0,
                    'visitante_derrotas_fora': 0,
                    'visitante_pontos': 0,
                    'visitante_jogos': 0
                })
            
            # Features de sentimento
            if not sent_casa.empty:
                casa_sent = sent_casa.iloc[0]
                features.update({
                    'casa_sentimento_medio_noticias': casa_sent.get('sentimento_medio_noticias', 0.0),
                    'casa_sentimento_medio_posts': casa_sent.get('sentimento_medio_posts', 0.0),
                    'casa_media_curtidas': casa_sent.get('media_curtidas', 0.0),
                    'casa_media_comentarios': casa_sent.get('media_comentarios', 0.0),
                    'casa_media_compartilhamentos': casa_sent.get('media_compartilhamentos', 0.0)
                })
            else:
                features.update({
                    'casa_sentimento_medio_noticias': 0.0,
                    'casa_sentimento_medio_posts': 0.0,
                    'casa_media_curtidas': 0.0,
                    'casa_media_comentarios': 0.0,
                    'casa_media_compartilhamentos': 0.0
                })
            
            if not sent_visitante.empty:
                visitante_sent = sent_visitante.iloc[0]
                features.update({
                    'visitante_sentimento_medio_noticias': visitante_sent.get('sentimento_medio_noticias', 0.0),
                    'visitante_sentimento_medio_posts': visitante_sent.get('sentimento_medio_posts', 0.0),
                    'visitante_media_curtidas': visitante_sent.get('media_curtidas', 0.0),
                    'visitante_media_comentarios': visitante_sent.get('media_comentarios', 0.0),
                    'visitante_media_compartilhamentos': visitante_sent.get('media_compartilhamentos', 0.0)
                })
            else:
                features.update({
                    'visitante_sentimento_medio_noticias': 0.0,
                    'visitante_sentimento_medio_posts': 0.0,
                    'visitante_media_curtidas': 0.0,
                    'visitante_media_comentarios': 0.0,
                    'visitante_media_compartilhamentos': 0.0
                })
            
            # Features de histórico de confrontos
            if not historico_confrontos.empty:
                # Últimos 5 confrontos
                ultimos_confrontos = historico_confrontos.head(5)
                
                # Estatísticas dos últimos confrontos
                features.update({
                    'historico_vitorias_clube_referencia': len(ultimos_confrontos[ultimos_confrontos['resultado_clube_referencia'] == 'vitoria']),
                    'historico_empates': len(ultimos_confrontos[ultimos_confrontos['resultado_clube_referencia'] == 'empate']),
                    'historico_derrotas_clube_referencia': len(ultimos_confrontos[ultimos_confrontos['resultado_clube_referencia'] == 'derrota']),
                    'historico_media_gols_clube_referencia': ultimos_confrontos['gols_clube_referencia'].mean(),
                    'historico_media_gols_adversario': ultimos_confrontos['gols_adversario'].mean(),
                    'historico_media_total_gols': ultimos_confrontos['total_gols'].mean()
                })
            else:
                features.update({
                    'historico_vitorias_clube_referencia': 0,
                    'historico_empates': 0,
                    'historico_derrotas_clube_referencia': 0,
                    'historico_media_gols_clube_referencia': 0.0,
                    'historico_media_gols_adversario': 0.0,
                    'historico_media_total_gols': 0.0
                })
            
            # Features derivadas
            features['diferenca_aproveitamento'] = features['casa_aproveitamento'] - features['visitante_aproveitamento']
            features['diferenca_saldo_gols'] = features['casa_saldo_gols'] - features['visitante_saldo_gols']
            features['diferenca_gols_marcados_por_jogo'] = features['casa_gols_marcados_por_jogo'] - features['visitante_gols_marcados_por_jogo']
            features['diferenca_gols_sofridos_por_jogo'] = features['casa_gols_sofridos_por_jogo'] - features['visitante_gols_sofridos_por_jogo']
            
            # Features de sentimento agregadas
            features['diferenca_sentimento_noticias'] = features['casa_sentimento_medio_noticias'] - features['visitante_sentimento_medio_noticias']
            features['diferenca_sentimento_posts'] = features['casa_sentimento_medio_posts'] - features['visitante_sentimento_medio_posts']
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar features da partida: {e}")
            return {}
    
    def preparar_dataset_treinamento(self, data_inicio: Optional[datetime] = None,
                                   data_fim: Optional[datetime] = None) -> pd.DataFrame:
        """
        Prepara dataset completo para treinamento de modelos.
        
        Args:
            data_inicio: Data de início para filtrar partidas
            data_fim: Data de fim para filtrar partidas
            
        Returns:
            DataFrame com features e targets para treinamento
        """
        try:
            logger.info("🚀 Iniciando preparação do dataset de treinamento...")
            
            # Carrega dados básicos
            df_partidas = self.carregar_dados_partidas(data_inicio, data_fim)
            if df_partidas.empty:
                logger.error("❌ Nenhuma partida encontrada para preparar dataset")
                return pd.DataFrame()
            
            # Carrega estatísticas dos clubes
            estatisticas_clubes = self.carregar_estatisticas_clubes()
            if estatisticas_clubes.empty:
                logger.error("❌ Nenhuma estatística de clube encontrada")
                return pd.DataFrame()
            
            # Carrega dados de sentimento
            sentimento_clubes = self.carregar_sentimento_clubes()
            if sentimento_clubes.empty:
                logger.warning("⚠️ Nenhum dado de sentimento encontrado, usando valores padrão")
                sentimento_clubes = pd.DataFrame()
            
            # Lista para armazenar features de todas as partidas
            todas_features = []
            
            # Processa cada partida
            for idx, partida in df_partidas.iterrows():
                try:
                    # Carrega histórico de confrontos
                    historico_confrontos = self.carregar_historico_confrontos(
                        partida['clube_casa_id'], 
                        partida['clube_visitante_id'],
                        partida['data_partida']
                    )
                    
                    # Cria features para a partida
                    features = self.criar_features_partida(
                        partida, estatisticas_clubes, sentimento_clubes, historico_confrontos
                    )
                    
                    if features:
                        # Adiciona target (resultado da partida)
                        features['target_resultado'] = partida['resultado']
                        features['target_total_gols'] = partida['total_gols']
                        features['target_ambos_marcam'] = 1 if (partida['gols_casa'] > 0 and partida['gols_visitante'] > 0) else 0
                        
                        todas_features.append(features)
                    
                    # Log de progresso
                    if (idx + 1) % 100 == 0:
                        logger.info(f"📊 Processadas {idx + 1}/{len(df_partidas)} partidas")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao processar partida {partida['id']}: {e}")
                    continue
            
            if not todas_features:
                logger.error("❌ Nenhuma feature foi criada")
                return pd.DataFrame()
            
            # Converte para DataFrame
            df_features = pd.DataFrame(todas_features)
            
            # Remove colunas com muitos valores nulos
            colunas_com_nulos = df_features.columns[df_features.isnull().sum() > len(df_features) * 0.5]
            if not colunas_com_nulos.empty:
                logger.warning(f"⚠️ Removendo colunas com muitos valores nulos: {colunas_com_nulos.tolist()}")
                df_features = df_features.drop(columns=colunas_com_nulos)
            
            # Preenche valores nulos restantes
            df_features = df_features.fillna(0)
            
            # Remove colunas não numéricas
            colunas_nao_numericas = df_features.select_dtypes(include=['object', 'datetime64']).columns
            if not colunas_nao_numericas.empty:
                logger.info(f"ℹ️ Removendo colunas não numéricas: {colunas_nao_numericas.tolist()}")
                df_features = df_features.drop(columns=colunas_nao_numericas)
            
            logger.info(f"✅ Dataset preparado com sucesso: {df_features.shape}")
            logger.info(f"📊 Features: {df_features.shape[1] - 3}")  # -3 para os targets
            logger.info(f"📊 Partidas: {df_features.shape[0]}")
            
            return df_features
            
        except Exception as e:
            logger.error(f"❌ Erro fatal na preparação do dataset: {e}")
            return pd.DataFrame()
    
    def _calcular_resultado(self, gols_casa: int, gols_visitante: int) -> str:
        """Calcula o resultado de uma partida."""
        if gols_casa > gols_visitante:
            return 'casa'
        elif gols_casa < gols_visitante:
            return 'visitante'
        else:
            return 'empate'
    
    def _calcular_resultado_clube_referencia(self, gols_clube: int, gols_adversario: int) -> str:
        """Calcula o resultado para o clube de referência."""
        if gols_clube > gols_adversario:
            return 'vitoria'
        elif gols_clube < gols_adversario:
            return 'derrota'
        else:
            return 'empate'


def executar_preparacao_dados():
    """Função principal para executar a preparação de dados."""
    try:
        from Coleta_de_dados.database.config import SessionLocal
        
        logger.info("🚀 Iniciando preparação de dados para ML...")
        
        # Cria sessão do banco
        db = SessionLocal()
        
        try:
            # Cria preparador
            preparador = PreparadorDadosML(db)
            
            # Prepara dataset (últimos 2 anos)
            data_fim = datetime.now()
            data_inicio = data_fim - timedelta(days=730)
            
            dataset = preparador.preparar_dataset_treinamento(data_inicio, data_fim)
            
            if not dataset.empty:
                logger.info("✅ Dataset preparado com sucesso!")
                logger.info(f"📊 Shape: {dataset.shape}")
                logger.info(f"📊 Colunas: {list(dataset.columns)}")
                
                # Salva dataset
                dataset.to_csv('dataset_treinamento_ml.csv', index=False)
                logger.info("💾 Dataset salvo em 'dataset_treinamento_ml.csv'")
                
                return dataset
            else:
                logger.error("❌ Falha na preparação do dataset")
                return None
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erro fatal na preparação de dados: {e}")
        raise


if __name__ == "__main__":
    executar_preparacao_dados()
