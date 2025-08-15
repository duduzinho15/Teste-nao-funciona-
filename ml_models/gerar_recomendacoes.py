#!/usr/bin/env python3
"""
Módulo de geração de recomendações de apostas usando modelos de Machine Learning treinados.
Gera previsões para partidas futuras e calcula odds justas e ratings de confiança.
"""

import pandas as pd
import numpy as np
import logging
import pickle
import os
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeradorRecomendacoes:
    """Gerador de recomendações de apostas usando modelos de ML treinados."""
    
    def __init__(self, db_session: Session, diretorio_modelos: str = 'modelos_treinados'):
        """
        Inicializa o gerador de recomendações.
        
        Args:
            db_session: Sessão do banco de dados
            diretorio_modelos: Diretório onde os modelos estão salvos
        """
        self.db_session = db_session
        self.diretorio_modelos = diretorio_modelos
        self.modelos = {}
        self.scalers = {}
        self.label_encoders = {}
        self.preparador_dados = None
        
        # Carrega modelos treinados
        self._carregar_modelos()
        
        logger.info("🎯 Gerador de recomendações inicializado")
    
    def _carregar_modelos(self) -> bool:
        """Carrega os modelos treinados."""
        try:
            if not os.path.exists(self.diretorio_modelos):
                logger.error(f"❌ Diretório de modelos não encontrado: {self.diretorio_modelos}")
                return False
            
            # Tipos de modelos disponíveis
            tipos_modelos = ['resultado_1x2', 'over_under_2_5', 'ambos_marcam']
            
            for tipo in tipos_modelos:
                caminho_modelo = os.path.join(self.diretorio_modelos, f'{tipo}_modelo.pkl')
                caminho_scaler = os.path.join(self.diretorio_modelos, f'{tipo}_scaler.pkl')
                caminho_le = os.path.join(self.diretorio_modelos, f'{tipo}_label_encoder.pkl')
                
                if all(os.path.exists(p) for p in [caminho_modelo, caminho_scaler, caminho_le]):
                    # Carrega modelo
                    with open(caminho_modelo, 'rb') as f:
                        self.modelos[tipo] = pickle.load(f)
                    
                    # Carrega scaler
                    with open(caminho_scaler, 'rb') as f:
                        self.scalers[tipo] = pickle.load(f)
                    
                    # Carrega label encoder
                    with open(caminho_le, 'rb') as f:
                        self.label_encoders[tipo] = pickle.load(f)
                    
                    logger.info(f"✅ Modelo {tipo} carregado com sucesso")
                else:
                    logger.warning(f"⚠️ Arquivos do modelo {tipo} não encontrados")
            
            return len(self.modelos) > 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelos: {e}")
            return False
    
    def carregar_partidas_futuras(self, dias_futuros: int = 7) -> pd.DataFrame:
        """
        Carrega partidas futuras que ainda não têm recomendações.
        
        Args:
            dias_futuros: Número de dias no futuro para buscar partidas
            
        Returns:
            DataFrame com partidas futuras
        """
        try:
            data_futura = datetime.now() + timedelta(days=dias_futuros)
            
            # Query para partidas futuras
            query = """
                SELECT 
                    p.id,
                    p.data_partida,
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
                WHERE p.status = 'agendada'
                    AND p.data_partida BETWEEN :data_inicio AND :data_futura
                    AND p.id NOT IN (
                        SELECT DISTINCT partida_id 
                        FROM recomendacoes_apostas 
                        WHERE partida_id IS NOT NULL
                    )
                ORDER BY p.data_partida ASC
            """
            
            data_inicio = datetime.now()
            
            result = self.db_session.execute(text(query), {
                'data_inicio': data_inicio,
                'data_futura': data_futura
            })
            
            partidas = result.fetchall()
            
            if not partidas:
                logger.warning("⚠️ Nenhuma partida futura encontrada para gerar recomendações")
                return pd.DataFrame()
            
            # Converte para DataFrame
            df_partidas = pd.DataFrame(partidas)
            logger.info(f"✅ {len(df_partidas)} partidas futuras carregadas")
            
            return df_partidas
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar partidas futuras: {e}")
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
                    COUNT(*) as total_noticias
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
                    CASE 
                        WHEN p.clube_casa_id = :clube_casa_id THEN p.gols_casa
                        ELSE p.gols_visitante
                    END as gols_clube_referencia,
                    CASE 
                        WHEN p.clube_casa_id = :clube_casa_id THEN p.gols_visitante
                        ELSE p.gols_casa
                    END as gols_adversario
                FROM partidas p
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
    
    def gerar_recomendacao_partida(self, partida: pd.Series, estatisticas_clubes: pd.DataFrame,
                                  sentimento_clubes: pd.DataFrame) -> Dict[str, Any]:
        """
        Gera recomendação completa para uma partida.
        
        Args:
            partida: Série com dados da partida
            estatisticas_clubes: DataFrame com estatísticas dos clubes
            sentimento_clubes: DataFrame com dados de sentimento
            
        Returns:
            Dicionário com recomendação completa
        """
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
            
            if not features:
                return {}
            
            # Remove colunas não úteis para ML
            colunas_remover = ['partida_id', 'data_partida', 'clube_casa_id', 'clube_visitante_id', 'competicao_id']
            features_ml = {k: v for k, v in features.items() if k not in colunas_remover}
            
            # Converte para DataFrame
            df_features = pd.DataFrame([features_ml])
            
            # Gera predições para cada tipo de aposta
            recomendacoes = {}
            
            # Predição para resultado 1X2
            if 'resultado_1x2' in self.modelos:
                pred_1x2 = self._fazer_predicao_modelo(df_features, 'resultado_1x2')
                if pred_1x2:
                    recomendacoes['resultado_1x2'] = pred_1x2
            
            # Predição para Over/Under
            if 'over_under_2_5' in self.modelos:
                pred_over_under = self._fazer_predicao_modelo(df_features, 'over_under_2_5')
                if pred_over_under:
                    recomendacoes['over_under_2_5'] = pred_over_under
            
            # Predição para Ambos Marcam
            if 'ambos_marcam' in self.modelos:
                pred_ambos = self._fazer_predicao_modelo(df_features, 'ambos_marcam')
                if pred_ambos:
                    recomendacoes['ambos_marcam'] = pred_ambos
            
            # Calcula odds justas e ratings
            for tipo_aposta, predicao in recomendacoes.items():
                odds_justa, rating = self._calcular_odds_rating(predicao)
                predicao['odd_justa'] = odds_justa
                predicao['rating'] = rating
            
            resultado = {
                'partida_id': partida['id'],
                'clube_casa': partida['clube_casa'],
                'clube_visitante': partida['clube_visitante'],
                'data_partida': partida['data_partida'],
                'competicao': partida['competicao'],
                'recomendacoes': recomendacoes,
                'features_utilizadas': list(features_ml.keys()),
                'data_geracao': datetime.now().isoformat()
            }
            
            logger.info(f"🎯 Recomendação gerada para partida {partida['id']}: {partida['clube_casa']} vs {partida['clube_visitante']}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar recomendação para partida {partida['id']}: {e}")
            return {}
    
    def _fazer_predicao_modelo(self, features: pd.DataFrame, tipo_aposta: str) -> Dict[str, Any]:
        """
        Faz predição usando um modelo específico.
        
        Args:
            features: Features da partida
            tipo_aposta: Tipo de aposta
            
        Returns:
            Dicionário com predição
        """
        try:
            if tipo_aposta not in self.modelos:
                return {}
            
            # Escala as features
            features_scaled = self.scalers[tipo_aposta].transform(features)
            
            # Faz predição
            modelo = self.modelos[tipo_aposta]
            predicao = modelo.predict(features_scaled)
            probabilidades = modelo.predict_proba(features_scaled)
            
            # Decodifica predição se necessário
            if tipo_aposta in self.label_encoders:
                predicao_decodificada = self.label_encoders[tipo_aposta].inverse_transform(predicao)
            else:
                predicao_decodificada = predicao
            
            resultado = {
                'predicao': predicao_decodificada[0] if len(predicao_decodificada) == 1 else predicao_decodificada,
                'probabilidades': probabilidades[0] if len(probabilidades) == 1 else probabilidades,
                'confianca': float(np.max(probabilidades)),
                'modelo_utilizado': modelo.__class__.__name__
            }
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro ao fazer predição com modelo {tipo_aposta}: {e}")
            return {}
    
    def _calcular_odds_rating(self, predicao: Dict[str, Any]) -> Tuple[float, int]:
        """
        Calcula odds justa e rating baseado na predição.
        
        Args:
            predicao: Dicionário com predição
            
        Returns:
            Tuple com odds justa e rating
        """
        try:
            confianca = predicao.get('confianca', 0.5)
            
            # Calcula odds justa (inverso da probabilidade)
            odds_justa = 1.0 / confianca if confianca > 0 else 10.0
            
            # Calcula rating (1-10)
            rating = int(confianca * 10)
            rating = max(1, min(10, rating))  # Limita entre 1 e 10
            
            return odds_justa, rating
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular odds e rating: {e}")
            return 2.0, 5  # Valores padrão
    
    def _calcular_resultado_clube_referencia(self, gols_clube: int, gols_adversario: int) -> str:
        """Calcula o resultado para o clube de referência."""
        if gols_clube > gols_adversario:
            return 'vitoria'
        elif gols_clube < gols_adversario:
            return 'derrota'
        else:
            return 'empate'
    
    def gerar_recomendacoes_lote(self, dias_futuros: int = 7) -> List[Dict[str, Any]]:
        """
        Gera recomendações para todas as partidas futuras.
        
        Args:
            dias_futuros: Número de dias no futuro para buscar partidas
            
        Returns:
            Lista com todas as recomendações geradas
        """
        try:
            logger.info(f"🚀 Iniciando geração de recomendações para próximos {dias_futuros} dias...")
            
            # Carrega partidas futuras
            partidas_futuras = self.carregar_partidas_futuras(dias_futuros)
            if partidas_futuras.empty:
                logger.warning("⚠️ Nenhuma partida futura encontrada")
                return []
            
            # Carrega dados necessários
            estatisticas_clubes = self.carregar_estatisticas_clubes()
            sentimento_clubes = self.carregar_sentimento_clubes()
            
            if estatisticas_clubes.empty:
                logger.error("❌ Nenhuma estatística de clube encontrada")
                return []
            
            # Lista para armazenar recomendações
            todas_recomendacoes = []
            
            # Gera recomendação para cada partida
            for idx, partida in partidas_futuras.iterrows():
                try:
                    recomendacao = self.gerar_recomendacao_partida(
                        partida, estatisticas_clubes, sentimento_clubes
                    )
                    
                    if recomendacao:
                        todas_recomendacoes.append(recomendacao)
                    
                    # Log de progresso
                    if (idx + 1) % 10 == 0:
                        logger.info(f"📊 Processadas {idx + 1}/{len(partidas_futuras)} partidas")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao processar partida {partida['id']}: {e}")
                    continue
            
            logger.info(f"✅ {len(todas_recomendacoes)} recomendações geradas com sucesso")
            
            return todas_recomendacoes
            
        except Exception as e:
            logger.error(f"❌ Erro fatal na geração de recomendações: {e}")
            return []
    
    def salvar_recomendacoes_banco(self, recomendacoes: List[Dict[str, Any]]) -> bool:
        """
        Salva as recomendações geradas no banco de dados.
        
        Args:
            recomendacoes: Lista com recomendações
            
        Returns:
            True se todas as recomendações foram salvas com sucesso
        """
        try:
            if not recomendacoes:
                logger.warning("⚠️ Nenhuma recomendação para salvar")
                return True
            
            logger.info(f"💾 Salvando {len(recomendacoes)} recomendações no banco...")
            
            # Insere cada recomendação
            for recomendacao in recomendacoes:
                try:
                    # Insere recomendação principal
                    query_principal = """
                        INSERT INTO recomendacoes_apostas 
                        (partida_id, clube_casa, clube_visitante, data_partida, competicao, 
                         features_utilizadas, data_geracao, status)
                        VALUES (:partida_id, :clube_casa, :clube_visitante, :data_partida, :competicao,
                                :features_utilizadas, :data_geracao, 'ativa')
                        RETURNING id
                    """
                    
                    result = self.db_session.execute(text(query_principal), {
                        'partida_id': recomendacao['partida_id'],
                        'clube_casa': recomendacao['clube_casa'],
                        'clube_visitante': recomendacao['clube_visitante'],
                        'data_partida': recomendacao['data_partida'],
                        'competicao': recomendacao['competicao'],
                        'features_utilizadas': ','.join(recomendacao['features_utilizadas']),
                        'data_geracao': recomendacao['data_geracao']
                    })
                    
                    recomendacao_id = result.fetchone()[0]
                    
                    # Insere detalhes das recomendações
                    for tipo_aposta, detalhes in recomendacao['recomendacoes'].items():
                        query_detalhes = """
                            INSERT INTO detalhes_recomendacoes
                            (recomendacao_id, tipo_aposta, predicao, probabilidade, confianca,
                             odd_justa, rating, modelo_utilizado)
                            VALUES (:recomendacao_id, :tipo_aposta, :predicao, :probabilidade, :confianca,
                                    :odd_justa, :rating, :modelo_utilizado)
                        """
                        
                        # Calcula probabilidade média
                        prob_media = np.mean(detalhes['probabilidades'])
                        
                        self.db_session.execute(text(query_detalhes), {
                            'recomendacao_id': recomendacao_id,
                            'tipo_aposta': tipo_aposta,
                            'predicao': str(detalhes['predicao']),
                            'probabilidade': float(prob_media),
                            'confianca': detalhes['confianca'],
                            'odd_justa': detalhes['odd_justa'],
                            'rating': detalhes['rating'],
                            'modelo_utilizado': detalhes['modelo_utilizado']
                        })
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao salvar recomendação {recomendacao['partida_id']}: {e}")
                    continue
            
            # Commit das transações
            self.db_session.commit()
            logger.info("✅ Todas as recomendações salvas no banco com sucesso!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar recomendações no banco: {e}")
            self.db_session.rollback()
            return False


def executar_geracao_recomendacoes():
    """Função principal para executar a geração de recomendações."""
    try:
        from Coleta_de_dados.database.config import SessionLocal
        
        logger.info("🚀 Iniciando geração de recomendações...")
        
        # Cria sessão do banco
        db = SessionLocal()
        
        try:
            # Cria gerador
            gerador = GeradorRecomendacoes(db)
            
            # Gera recomendações para próximos 7 dias
            recomendacoes = gerador.gerar_recomendacoes_lote(dias_futuros=7)
            
            if recomendacoes:
                logger.info(f"✅ {len(recomendacoes)} recomendações geradas")
                
                # Salva no banco
                if gerador.salvar_recomendacoes_banco(recomendacoes):
                    logger.info("💾 Recomendações salvas no banco com sucesso!")
                else:
                    logger.error("❌ Erro ao salvar recomendações no banco")
                
                return recomendacoes
            else:
                logger.warning("⚠️ Nenhuma recomendação foi gerada")
                return []
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erro fatal na geração de recomendações: {e}")
        raise


if __name__ == "__main__":
    executar_geracao_recomendacoes()
