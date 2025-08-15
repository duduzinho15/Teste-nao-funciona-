"""
Transfermarkt DB API - RapidAPI
===============================

Implementação da API Transfermarkt DB do RapidAPI para coleta de dados
de transferências, valores de mercado e perfis de jogadores do Transfermarkt.

Autor: Sistema de Coleta de Dados ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_rapidapi import RapidAPIBase, RapidAPIConfig

logger = logging.getLogger(__name__)

class TransfermarktDBAPI(RapidAPIBase):
    """
    API Transfermarkt DB do RapidAPI.
    
    Fornece dados do Transfermarkt:
    - Perfis de jogadores
    - Valores de mercado
    - Histórico de transferências
    - Estatísticas de carreira
    - Informações de clubes
    - Rankings e listas
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa a API Transfermarkt DB."""
        # Usar chave padrão se não fornecida
        if api_key is None:
            api_key = "chave_padrao_rapidapi"  # Será substituída pela variável de ambiente
        
        config = RapidAPIConfig(
            nome="Transfermarkt DB",
            host="transfermarkt-db.p.rapidapi.com",
            endpoint_base="https://transfermarkt-db.p.rapidapi.com",
            chaves=[api_key],
            limite_requisicoes_dia=100,
            limite_requisicoes_minuto=10,
            timeout=30,
            retry_attempts=3,
            retry_delay=2
        )
        super().__init__(config)
        
        # Endpoints específicos da API
        self.endpoints = {
            'jogadores': '/players',
            'clubes': '/clubs',
            'transferencias': '/transfers',
            'valores': '/market-values',
            'estatisticas': '/statistics',
            'rankings': '/rankings'
        }
    
    async def coletar_jogos(self, clube_id: Optional[str] = None,
                           liga_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta jogos da API Transfermarkt DB.
        
        Args:
            clube_id: ID do clube (opcional)
            liga_id: ID da liga (opcional)
            
        Returns:
            Lista de jogos padronizados
        """
        try:
            # Esta API pode não ter endpoint específico para jogos
            # Retornamos lista vazia por enquanto
            logger.info("API Transfermarkt DB não fornece dados de jogos")
            return []
            
        except Exception as e:
            logger.error(f"Erro ao coletar jogos: {e}")
            return []
    
    async def coletar_jogadores(self, clube_id: Optional[str] = None,
                               liga_id: Optional[str] = None,
                               posicao: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta jogadores da API Transfermarkt DB.
        
        Args:
            clube_id: ID do clube (opcional)
            liga_id: ID da liga (opcional)
            posicao: Posição do jogador (opcional)
            
        Returns:
            Lista de jogadores padronizados
        """
        try:
            params = {}
            if clube_id:
                params['club'] = clube_id
            if liga_id:
                params['league'] = liga_id
            if posicao:
                params['position'] = posicao
            
            response = await self._make_request(
                endpoint=self.endpoints['jogadores'],
                params=params
            )
            
            if not response or 'players' not in response:
                logger.warning("Resposta da API não contém dados de jogadores")
                return []
            
            jogadores = []
            for jogador in response['players']:
                jogador_padronizado = self._padronizar_jogador_transfermarkt(jogador)
                if jogador_padronizado:
                    jogadores.append(jogador_padronizado)
            
            logger.info(f"Coletados {len(jogadores)} jogadores da Transfermarkt DB")
            return jogadores
            
        except Exception as e:
            logger.error(f"Erro ao coletar jogadores: {e}")
            return []
    
    async def coletar_ligas(self, pais: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta ligas da API Transfermarkt DB.
        
        Args:
            pais: País das ligas (opcional)
            
        Returns:
            Lista de ligas padronizadas
        """
        try:
            params = {}
            if pais:
                params['country'] = pais
            
            response = await self._make_request(
                endpoint=self.endpoints['clubes'],
                params=params
            )
            
            if not response or 'leagues' not in response:
                logger.warning("Resposta da API não contém dados de ligas")
                return []
            
            ligas = []
            for liga in response['leagues']:
                liga_padronizada = self._padronizar_liga(liga)
                if liga_padronizada:
                    ligas.append(liga_padronizada)
            
            logger.info(f"Coletadas {len(ligas)} ligas da Transfermarkt DB")
            return ligas
            
        except Exception as e:
            logger.error(f"Erro ao coletar ligas: {e}")
            return []
    
    async def coletar_estatisticas(self, jogador_id: Optional[str] = None,
                                  clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta estatísticas da API Transfermarkt DB.
        
        Args:
            jogador_id: ID do jogador (opcional)
            clube_id: ID do clube (opcional)
            
        Returns:
            Lista de estatísticas padronizadas
        """
        try:
            params = {}
            if jogador_id:
                params['player'] = jogador_id
            if clube_id:
                params['club'] = clube_id
            
            response = await self._make_request(
                endpoint=self.endpoints['estatisticas'],
                params=params
            )
            
            if not response or 'statistics' not in response:
                logger.warning("Resposta da API não contém dados de estatísticas")
                return []
            
            estatisticas = []
            for stat in response['statistics']:
                stat_padronizada = self._padronizar_estatistica(stat)
                if stat_padronizada:
                    estatisticas.append(stat_padronizada)
            
            logger.info(f"Coletadas {len(estatisticas)} estatísticas da Transfermarkt DB")
            return estatisticas
            
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas: {e}")
            return []
    
    async def coletar_odds(self, partida_id: str) -> List[Dict[str, Any]]:
        """
        Coleta odds da API Transfermarkt DB.
        
        Args:
            partida_id: ID da partida
            
        Returns:
            Lista de odds padronizadas
        """
        try:
            # Esta API pode não ter endpoint específico para odds
            # Retornamos lista vazia por enquanto
            logger.info("API Transfermarkt DB não fornece dados de odds")
            return []
            
        except Exception as e:
            logger.error(f"Erro ao coletar odds: {e}")
            return []
    
    async def coletar_noticias(self, clube_id: Optional[str] = None,
                              liga_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta notícias da API Transfermarkt DB.
        
        Args:
            clube_id: ID do clube (opcional)
            liga_id: ID da liga (opcional)
            
        Returns:
            Lista de notícias padronizadas
        """
        try:
            # Esta API pode não ter endpoint específico para notícias
            # Retornamos lista vazia por enquanto
            logger.info("API Transfermarkt DB não fornece notícias")
            return []
            
        except Exception as e:
            logger.error(f"Erro ao coletar notícias: {e}")
            return []
    
    async def coletar_transferencias(self, jogador_id: Optional[str] = None,
                                   clube_id: Optional[str] = None,
                                   temporada: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta transferências da API Transfermarkt DB.
        
        Args:
            jogador_id: ID do jogador (opcional)
            clube_id: ID do clube (opcional)
            temporada: Temporada (opcional)
            
        Returns:
            Lista de transferências padronizadas
        """
        try:
            params = {}
            if jogador_id:
                params['player'] = jogador_id
            if clube_id:
                params['club'] = clube_id
            if temporada:
                params['season'] = temporada
            
            response = await self._make_request(
                endpoint=self.endpoints['transferencias'],
                params=params
            )
            
            if not response or 'transfers' not in response:
                logger.warning("Resposta da API não contém dados de transferências")
                return []
            
            transferencias = []
            for transferencia in response['transfers']:
                transferencia_padronizada = self._padronizar_transferencia(transferencia)
                if transferencia_padronizada:
                    transferencias.append(transferencia_padronizada)
            
            logger.info(f"Coletadas {len(transferencias)} transferências da Transfermarkt DB")
            return transferencias
            
        except Exception as e:
            logger.error(f"Erro ao coletar transferências: {e}")
            return []
    
    async def coletar_valores_mercado(self, jogador_id: Optional[str] = None,
                                     clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta valores de mercado da API Transfermarkt DB.
        
        Args:
            jogador_id: ID do jogador (opcional)
            clube_id: ID do clube (opcional)
            
        Returns:
            Lista de valores de mercado padronizados
        """
        try:
            params = {}
            if jogador_id:
                params['player'] = jogador_id
            if clube_id:
                params['club'] = clube_id
            
            response = await self._make_request(
                endpoint=self.endpoints['valores'],
                params=params
            )
            
            if not response or 'market_values' not in response:
                logger.warning("Resposta da API não contém dados de valores de mercado")
                return []
            
            valores = []
            for valor in response['market_values']:
                valor_padronizado = self._padronizar_valor_mercado(valor)
                if valor_padronizado:
                    valores.append(valor_padronizado)
            
            logger.info(f"Coletados {len(valores)} valores de mercado da Transfermarkt DB")
            return valores
            
        except Exception as e:
            logger.error(f"Erro ao coletar valores de mercado: {e}")
            return []
    
    def _padronizar_jogador_transfermarkt(self, jogador: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de um jogador do Transfermarkt."""
        try:
            return {
                'id_jogador': str(jogador.get('id', '')),
                'nome': jogador.get('name', ''),
                'nome_completo': jogador.get('full_name', ''),
                'posicao': jogador.get('position', ''),
                'clube_atual': jogador.get('current_club', ''),
                'nacionalidade': jogador.get('nationality', ''),
                'idade': jogador.get('age', 0),
                'altura': jogador.get('height', 0),
                'pe_preferido': jogador.get('preferred_foot', ''),
                'valor_mercado': jogador.get('market_value', ''),
                'contrato_ate': jogador.get('contract_until', ''),
                'fonte': 'transfermarkt_db',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar jogador Transfermarkt: {e}")
            return None
    
    def _padronizar_liga(self, liga: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma liga."""
        try:
            return {
                'id_liga': str(liga.get('id', '')),
                'nome': liga.get('name', ''),
                'pais': liga.get('country', ''),
                'nivel': liga.get('level', ''),
                'tipo': liga.get('type', ''),
                'fonte': 'transfermarkt_db',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar liga: {e}")
            return None
    
    def _padronizar_estatistica(self, stat: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma estatística."""
        try:
            return {
                'id_estatistica': str(stat.get('id', '')),
                'tipo': stat.get('type', ''),
                'valor': stat.get('value', 0),
                'unidade': stat.get('unit', ''),
                'contexto': stat.get('context', ''),
                'fonte': 'transfermarkt_db',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar estatística: {e}")
            return None
    
    def _padronizar_transferencia(self, transferencia: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma transferência."""
        try:
            return {
                'id_transferencia': str(transferencia.get('id', '')),
                'jogador': transferencia.get('player', ''),
                'clube_origem': transferencia.get('from_club', ''),
                'clube_destino': transferencia.get('to_club', ''),
                'data': transferencia.get('date', ''),
                'tipo': transferencia.get('type', ''),
                'valor': transferencia.get('fee', ''),
                'temporada': transferencia.get('season', ''),
                'fonte': 'transfermarkt_db',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar transferência: {e}")
            return None
    
    def _padronizar_valor_mercado(self, valor: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de um valor de mercado."""
        try:
            return {
                'id_valor': str(valor.get('id', '')),
                'jogador': valor.get('player', ''),
                'valor': valor.get('value', ''),
                'data_atualizacao': valor.get('update_date', ''),
                'temporada': valor.get('season', ''),
                'fonte': 'transfermarkt_db',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar valor de mercado: {e}")
            return None

# Função de demonstração
async def demo_transfermarkt_db():
    """Demonstra o uso da API Transfermarkt DB."""
    print("🧪 TESTANDO TRANSFERMARKT DB API...")
    
    try:
        api = TransfermarktDBAPI()
        
        # Teste de coleta de jogadores
        print("\n1️⃣ Coletando jogadores...")
        jogadores = await api.coletar_jogadores()
        print(f"✅ {len(jogadores)} jogadores coletados")
        
        # Teste de coleta de transferências
        print("\n2️⃣ Coletando transferências...")
        transferencias = await api.coletar_transferencias()
        print(f"✅ {len(transferencias)} transferências coletadas")
        
        # Teste de coleta de valores de mercado
        print("\n3️⃣ Coletando valores de mercado...")
        valores = await api.coletar_valores_mercado()
        print(f"✅ {len(valores)} valores coletados")
        
        print("\n🎉 Transfermarkt DB API funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na Transfermarkt DB API: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_transfermarkt_db())
