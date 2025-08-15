"""
Módulo de Geração de Recomendações de Apostas
Responsável por usar modelos ML treinados para gerar previsões e recomendações
"""

import pandas as pd
import numpy as np
import sqlite3
import joblib
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
from .preparacao_dados import PreparadorDadosML

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeradorRecomendacoes:
    def __init__(self, db_path: str = 'Banco_de_dados/aposta.db', 
                 models_dir: str = 'ml_models/saved_models'):
        self.db_path = db_path
        self.models_dir = models_dir
        self.modelo_carregado = None
        self.preparador = PreparadorDadosML(db_path)
        
    def _get_connection(self) -> sqlite3.Connection:
        """Estabelece conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def carregar_ultimo_modelo(self) -> bool:
        """
        Carrega o modelo mais recente treinado
        
        Returns:
            True se o modelo foi carregado com sucesso
        """
        try:
            # Listar arquivos de modelo
            if not os.path.exists(self.models_dir):
                logger.error(f"Diretório de modelos não encontrado: {self.models_dir}")
                return False
            
            arquivos_modelo = [f for f in os.listdir(self.models_dir) if f.endswith('.joblib')]
            
            if not arquivos_modelo:
                logger.error("Nenhum arquivo de modelo encontrado")
                return False
            
            # Encontrar o modelo mais recente
            arquivos_com_timestamp = []
            for arquivo in arquivos_modelo:
                try:
                    # Extrair timestamp do nome do arquivo
                    if 'modelo_apostas_' in arquivo:
                        # O formato é: modelo_apostas_gradient_boosting_20250814_061740.joblib
                        # Precisamos pegar as duas últimas partes para formar o timestamp completo
                        partes = arquivo.split('_')
                        if len(partes) >= 5:
                            # Últimas duas partes: 20250814 e 061740
                            data_str = partes[-2]  # 20250814
                            hora_str = partes[-1].replace('.joblib', '')  # 061740
                            timestamp_str = f"{data_str}_{hora_str}"  # 20250814_061740
                            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                            arquivos_com_timestamp.append((arquivo, timestamp))
                except Exception as e:
                    logger.warning(f"Erro ao processar arquivo {arquivo}: {e}")
                    continue
            
            if not arquivos_com_timestamp:
                logger.error("Não foi possível extrair timestamp dos arquivos de modelo")
                return False
            
            # Ordenar por timestamp e pegar o mais recente
            arquivos_com_timestamp.sort(key=lambda x: x[1], reverse=True)
            modelo_mais_recente = arquivos_com_timestamp[0][0]
            
            caminho_modelo = os.path.join(self.models_dir, modelo_mais_recente)
            logger.info(f"Carregando modelo: {modelo_mais_recente}")
            
            # Carregar modelo
            self.modelo_carregado = joblib.load(caminho_modelo)
            
            logger.info(f"✅ Modelo carregado com sucesso: {self.modelo_carregado['tipo_modelo']}")
            logger.info(f"📊 Accuracy: {self.modelo_carregado['accuracy']:.4f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False
    
    def _buscar_partidas_futuras(self, dias_futuros: int = 7) -> pd.DataFrame:
        """
        Busca partidas futuras sem recomendações
        
        Args:
            dias_futuros: Número de dias no futuro para buscar partidas
        
        Returns:
            DataFrame com partidas futuras
        """
        conn = self._get_connection()
        
        data_limite = datetime.now() + timedelta(days=dias_futuros)
        
        query = """
        SELECT 
            p.id,
            p.data,
            p.time_casa as nome_time_casa,
            p.time_visitante as nome_time_visitante
        FROM partidas p
        WHERE p.data > datetime('now')
        AND p.data <= ?
        AND p.id NOT IN (
            SELECT DISTINCT partida_id 
            FROM recomendacoes_apostas
        )
        ORDER BY p.data
        """
        
        partidas = pd.read_sql_query(query, conn, params=(data_limite,))
        conn.close()
        
        logger.info(f"Encontradas {len(partidas)} partidas futuras sem recomendações")
        return partidas
    
    def _preparar_features_partida(self, partida: pd.Series, partidas_historicas: pd.DataFrame) -> np.ndarray:
        """
        Prepara features para uma partida específica
        
        Args:
            partida: Dados da partida
            partidas_historicas: DataFrame com partidas históricas para cálculo de forma
        
        Returns:
            Array com features normalizadas
        """
        # Calcular forma dos times
        forma_casa = self.preparador._calcular_forma_time(
            partidas_historicas, partida['nome_time_casa'], partida['data']
        )
        forma_visitante = self.preparador._calcular_forma_time(
            partidas_historicas, partida['nome_time_visitante'], partida['data']
        )
        
        # Calcular sentimento dos times
        sentimento_casa = self.preparador._calcular_sentimento_time(
            partida['nome_time_casa'], partida['data']
        )
        sentimento_visitante = self.preparador._calcular_sentimento_time(
            partida['nome_time_visitante'], partida['data']
        )
        
        # Criar array de features na mesma ordem do treinamento
        features = np.array([
            forma_casa['forma_score'],
            forma_casa['vitorias'],
            forma_casa['empates'],
            forma_casa['derrotas'],
            forma_casa['gols_marcados'],
            forma_casa['gols_sofridos'],
            sentimento_casa['sentimento_medio'],
            sentimento_casa['confianca_sentimento'],
            forma_visitante['forma_score'],
            forma_visitante['vitorias'],
            forma_visitante['empates'],
            forma_visitante['derrotas'],
            forma_visitante['gols_marcados'],
            forma_visitante['gols_sofridos'],
            sentimento_visitante['sentimento_medio'],
            sentimento_visitante['confianca_sentimento'],
            forma_casa['forma_score'] - forma_visitante['forma_score'],
            sentimento_casa['sentimento_medio'] - sentimento_visitante['sentimento_medio']
        ])
        
        # Normalizar features usando o scaler do modelo
        features_scaled = self.modelo_carregado['scaler'].transform(features.reshape(1, -1))
        
        return features_scaled
    
    def _gerar_previsoes_partida(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Gera previsões para uma partida usando o modelo treinado
        
        Args:
            features: Features normalizadas da partida
        
        Returns:
            Dicionário com previsões e probabilidades
        """
        modelo = self.modelo_carregado['modelo']
        label_encoder = self.modelo_carregado['label_encoder']
        
        # Fazer previsão
        previsao_encoded = modelo.predict(features)[0]
        previsao = label_encoder.inverse_transform([previsao_encoded])[0]
        
        # Obter probabilidades
        probabilidades = modelo.predict_proba(features)[0]
        
        # Criar dicionário de resultados
        resultados = {}
        for i, classe in enumerate(label_encoder.classes_):
            resultados[classe] = {
                'probabilidade': float(probabilidades[i]),
                'odd_justa': 1.0 / probabilidades[i] if probabilidades[i] > 0 else 999.0
            }
        
        return {
            'previsao_principal': previsao,
            'probabilidade_principal': float(probabilidades[previsao_encoded]),
            'todas_probabilidades': resultados
        }
    
    def _salvar_recomendacao(self, partida_id: int, mercado: str, previsao: str, 
                            probabilidade: float, odd_justa: float = None) -> bool:
        """
        Salva uma recomendação no banco de dados
        
        Args:
            partida_id: ID da partida
            mercado: Tipo de mercado de aposta
            previsao: Previsão gerada
            probabilidade: Probabilidade da previsão
            odd_justa: Odd justa calculada
        
        Returns:
            True se salvou com sucesso
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO recomendacoes_apostas 
                (partida_id, mercado_aposta, previsao, probabilidade, odd_justa, data_geracao)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (partida_id, mercado, previsao, probabilidade, odd_justa, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar recomendação: {e}")
            return False
    
    def gerar_recomendacoes_partidas_futuras(self, dias_futuros: int = 7) -> List[Dict[str, Any]]:
        """
        Gera recomendações para partidas futuras
        
        Args:
            dias_futuros: Número de dias no futuro para analisar
        
        Returns:
            Lista com recomendações geradas
        """
        if not self.modelo_carregado:
            logger.error("Modelo não foi carregado")
            return []
        
        logger.info(f"🎯 Gerando recomendações para partidas dos próximos {dias_futuros} dias...")
        
        # Buscar partidas futuras
        partidas_futuras = self._buscar_partidas_futuras(dias_futuros)
        
        if partidas_futuras.empty:
            logger.info("Nenhuma partida futura encontrada para gerar recomendações")
            return []
        
        # Buscar partidas históricas para cálculo de forma
        partidas_historicas = self.preparador.preparar_dataset_treinamento()
        
        if partidas_historicas.empty:
            logger.error("Não há dados históricos suficientes para calcular features")
            return []
        
        recomendacoes_geradas = []
        
        for _, partida in partidas_futuras.iterrows():
            try:
                logger.info(f"Analisando partida: {partida['nome_time_casa']} vs {partida['nome_time_visitante']}")
                
                # Preparar features
                features = self._preparar_features_partida(partida, partidas_historicas)
                
                # Gerar previsões
                previsoes = self._gerar_previsoes_partida(features)
                
                # Salvar recomendações para diferentes mercados
                recomendacoes_partida = []
                
                # 1. Resultado Final
                previsao_resultado = previsoes['previsao_principal']
                prob_resultado = previsoes['probabilidade_principal']
                odd_resultado = previsoes['todas_probabilidades'][previsao_resultado]['odd_justa']
                
                if self._salvar_recomendacao(
                    partida['id'], 'Resultado Final', previsao_resultado, 
                    prob_resultado, odd_resultado
                ):
                    recomendacoes_partida.append({
                        'mercado': 'Resultado Final',
                        'previsao': previsao_resultado,
                        'probabilidade': prob_resultado,
                        'odd_justa': odd_resultado
                    })
                
                # 2. Ambas Marcam (baseado em estatísticas históricas)
                # Calcular probabilidade baseada em gols marcados/sofridos
                forma_casa = self.preparador._calcular_forma_time(
                    partidas_historicas, partida['nome_time_casa'], partida['data']
                )
                forma_visitante = self.preparador._calcular_forma_time(
                    partidas_historicas, partida['nome_time_visitante'], partida['data']
                )
                
                # Probabilidade simplificada baseada em forma de ataque
                prob_ambas_marcam = min(0.8, max(0.2, 
                    (forma_casa['gols_marcados'] + forma_visitante['gols_marcados']) / 20.0
                ))
                
                previsao_ambas = 'Sim' if prob_ambas_marcam > 0.5 else 'Não'
                
                if self._salvar_recomendacao(
                    partida['id'], 'Ambas Marcam', previsao_ambas, 
                    prob_ambas_marcam, 1.0/prob_ambas_marcam
                ):
                    recomendacoes_partida.append({
                        'mercado': 'Ambas Marcam',
                        'previsao': previsao_ambas,
                        'probabilidade': prob_ambas_marcam,
                        'odd_justa': 1.0/prob_ambas_marcam
                    })
                
                # 3. Total de Gols (baseado em estatísticas históricas)
                media_gols_casa = forma_casa['gols_marcados'] / max(1, forma_casa['vitorias'] + forma_casa['empates'] + forma_casa['derrotas'])
                media_gols_visitante = forma_visitante['gols_marcados'] / max(1, forma_visitante['vitorias'] + forma_visitante['empates'] + forma_visitante['derrotas'])
                
                total_esperado = media_gols_casa + media_gols_visitante
                previsao_total = 'Acima de 2.5' if total_esperado > 2.5 else 'Abaixo de 2.5'
                prob_total = min(0.9, max(0.1, total_esperado / 5.0))
                
                if self._salvar_recomendacao(
                    partida['id'], 'Total de Gols', previsao_total, 
                    prob_total, 1.0/prob_total
                ):
                    recomendacoes_partida.append({
                        'mercado': 'Total de Gols',
                        'previsao': previsao_total,
                        'probabilidade': prob_total,
                        'odd_justa': 1.0/prob_total
                    })
                
                # Adicionar à lista de recomendações
                recomendacoes_geradas.append({
                    'partida_id': partida['id'],
                    'time_casa': partida['nome_time_casa'],
                    'time_visitante': partida['nome_time_visitante'],
                    'data_partida': partida['data'],
                    'recomendacoes': recomendacoes_partida
                })
                
                logger.info(f"✅ Recomendações geradas para partida {partida['id']}")
                
            except Exception as e:
                logger.error(f"Erro ao gerar recomendações para partida {partida['id']}: {e}")
                continue
        
        logger.info(f"🎯 Processo concluído: {len(recomendacoes_geradas)} partidas processadas")
        return recomendacoes_geradas
    
    def obter_recomendacoes_existentes(self, partida_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Busca recomendações existentes no banco
        
        Args:
            partida_id: ID da partida específica (opcional)
        
        Returns:
            Lista com recomendações
        """
        conn = self._get_connection()
        
        if partida_id:
            query = """
            SELECT r.*, p.data_partida, tc.nome as time_casa, tv.nome as time_visitante
            FROM recomendacoes_apostas r
            JOIN partidas p ON r.partida_id = p.id
            JOIN clubes tc ON p.time_casa_id = tc.id
            JOIN clubes tv ON p.time_visitante_id = tv.id
            WHERE r.partida_id = ?
            ORDER BY r.data_geracao DESC
            """
            recomendacoes = pd.read_sql_query(query, conn, params=(partida_id,))
        else:
            query = """
            SELECT r.*, p.data_partida, tc.nome as time_casa, tv.nome as time_visitante
            FROM recomendacoes_apostas r
            JOIN partidas p ON r.partida_id = p.id
            JOIN clubes tc ON p.time_casa_id = tc.id
            JOIN clubes tv ON p.time_visitante_id = tv.id
            ORDER BY r.data_geracao DESC
            LIMIT 100
            """
            recomendacoes = pd.read_sql_query(query, conn)
        
        conn.close()
        
        return recomendacoes.to_dict('records')

def main():
    """Função principal para demonstração"""
    print("🎯 Iniciando geração de recomendações...")
    
    gerador = GeradorRecomendacoes()
    
    # Carregar modelo
    if not gerador.carregar_ultimo_modelo():
        print("❌ Falha ao carregar modelo")
        return
    
    # Gerar recomendações
    recomendacoes = gerador.gerar_recomendacoes_partidas_futuras(dias_futuros=7)
    
    if recomendacoes:
        print(f"\n✅ Recomendações geradas com sucesso!")
        print(f"📊 Total de partidas processadas: {len(recomendacoes)}")
        
        # Mostrar algumas recomendações
        for rec in recomendacoes[:3]:
            print(f"\n🏆 {rec['time_casa']} vs {rec['time_visitante']}")
            print(f"📅 {rec['data_partida']}")
            for mercado_rec in rec['recomendacoes']:
                print(f"  {mercado_rec['mercado']}: {mercado_rec['previsao']} "
                      f"(Prob: {mercado_rec['probabilidade']:.2%}, "
                      f"Odd: {mercado_rec['odd_justa']:.2f})")
        
        # Buscar recomendações existentes
        print(f"\n📋 Recomendações existentes no banco:")
        existentes = gerador.obter_recomendacoes_existentes()
        print(f"Total: {len(existentes)} recomendações")
        
    else:
        print("❌ Nenhuma recomendação foi gerada")

if __name__ == "__main__":
    main()
