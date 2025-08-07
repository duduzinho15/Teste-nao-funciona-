#!/usr/bin/env python3
"""
FBREF INTEGRADO - VERSÃO SQLAlchemy ORM
======================================

Versão refatorada do script de coleta FBRef usando SQLAlchemy ORM.
Substitui todas as operações SQLite diretas por operações ORM.

Principais mudanças:
- Uso de SQLAlchemy ORM em vez de sqlite3
- Sessões de banco de dados com context managers
- Modelos ORM para todas as operações
- Melhor tratamento de erros e transações

Autor: Sistema de Migração de Banco de Dados
Data: 2025-08-03
Versão: 2.0 (ORM)
"""
from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from bs4 import BeautifulSoup, ResultSet, Tag
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

# Imports do sistema FBRef existente
from .fbref_utils import (
    BASE_URL,
    extrair_tabelas_da_pagina,
    fazer_requisicao,
    fechar_driver,
)
from .fbref_fallback_system import create_fallback_system

# Imports do sistema de banco de dados
from ...database import SessionLocal, db_manager
from ...database.models import (
    Clube,
    Competicao,
    EstatisticaPartida,
    LinkParaColeta,
    Partida,
)

# Import do módulo de estatísticas avançadas
from .advanced_stats import extract_advanced_match_stats

# --- CONFIGURAÇÕES ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))

logger = logging.getLogger(__name__)

# Sistema de fallback global
fallback_system = create_fallback_system(PROJECT_ROOT)

class FBRefCollectorORM:
    """Coletor FBRef usando SQLAlchemy ORM."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def coletar_competicoes(self) -> List[Dict[str, str]]:
        """
        Coleta competições com sistema de fallback robusto para lidar com rate limiting.
        """
        self.logger.info("Buscando lista de competições com sistema de fallback...")
        
        # Primeiro, verifica se há cache válido
        cached_competitions = fallback_system.get_cached_competitions()
        if cached_competitions:
            self.logger.info(f"Usando competições do cache: {len(cached_competitions)} competições")
            return cached_competitions
        
        # Verifica se o site está acessível rapidamente
        if not fallback_system.is_site_accessible():
            self.logger.warning("Site FBRef parece inacessível. Usando dados de fallback.")
            fallback_competitions = fallback_system.load_fallback_data()
            return fallback_competitions
        
        # Tenta fazer a requisição com timeout curto
        competicoes = []
        try:
            self.logger.info("Tentando requisição ao site FBRef...")
            
            # Timeout mais curto para evitar travamento
            start_time = time.time()
            soup = fazer_requisicao(f"{BASE_URL}/en/comps/")
            request_time = time.time() - start_time
            
            self.logger.info(f"Requisição completada em {request_time:.2f} segundos")
            
            if not soup:
                self.logger.warning("Requisição retornou None. Usando fallback.")
                return fallback_system.load_fallback_data()
            
            # Processa as tabelas normalmente
            tabelas_competicoes = soup.select("table.stats_table")
            if not tabelas_competicoes:
                self.logger.warning("Nenhuma tabela encontrada. Usando fallback.")
                return fallback_system.load_fallback_data()

            self.logger.debug(f"Encontradas {len(tabelas_competicoes)} tabelas de competições")
            
            for i, tabela in enumerate(tabelas_competicoes):
                self.logger.debug(f"Processando tabela {i+1}/{len(tabelas_competicoes)}")
                tbody = tabela.find('tbody')
                if not tbody:
                    continue
                    
                linhas = tbody.find_all('tr')
                
                for linha in linhas:
                    try:
                        th_cell = linha.find('th', {'data-stat': 'league_name'})
                        gender_cell = linha.find('td', {'data-stat': 'gender'})
                        
                        if not (th_cell and th_cell.find('a')):
                            continue
                            
                        link_tag = th_cell.find('a')
                        nome = link_tag.text.strip()
                        url = link_tag.get('href')
                        
                        if not url:
                            continue
                        
                        contexto = "Desconhecido"
                        if gender_cell:
                            gender_text = gender_cell.text.strip()
                            if gender_text == 'M':
                                contexto = "Masculino"
                            elif gender_text == 'F':
                                contexto = "Feminino"

                        # Resolve a ambiguidade da Serie A
                        if nome == "Serie A" and contexto == "Feminino":
                            nome = "Serie A (W)"
                        
                        if 'history' in url or 'tournaments' in url:
                            if not url.startswith('http'):
                                url = BASE_URL + url
                            
                            competicoes.append({
                                'nome': nome, 
                                'url': url, 
                                'contexto': contexto
                            })
                            
                    except Exception as e:
                        self.logger.warning(f"Erro ao processar linha da tabela: {e}")
                        continue
            
            # Cache das competições encontradas
            if competicoes:
                fallback_system.cache_competitions(competicoes)
                self.logger.info(f"Competições coletadas e armazenadas em cache: {len(competicoes)}")
            
            return competicoes
            
        except Exception as e:
            self.logger.error(f"Erro crítico na coleta de competições: {e}")
            self.logger.info("Usando dados de fallback devido ao erro")
            return fallback_system.load_fallback_data()

    def extrair_links_de_torneios_da_tabela(self, soup: BeautifulSoup) -> List[str]:
        """
        NOVO MÉTODO: Extrai links de temporadas de páginas de torneios que usam uma tabela de histórico.
        Este método foi criado para lidar com o layout de páginas como Copa do Mundo, Olimpíadas, etc.
        """
        links = []
        
        # Procura por tabelas que contenham histórico de torneios
        tabelas = soup.find_all('table', class_='stats_table')
        
        for tabela in tabelas:
            tbody = tabela.find('tbody')
            if not tbody:
                continue
                
            for linha in tbody.find_all('tr'):
                # Procura por células que contenham links para temporadas
                for cell in linha.find_all(['td', 'th']):
                    link = cell.find('a')
                    if link and link.get('href'):
                        href = link.get('href')
                        if any(keyword in href for keyword in ['/en/', 'stats', 'schedule']):
                            if not href.startswith('http'):
                                href = BASE_URL + href
                            links.append(href)
        
        return list(set(links))  # Remove duplicatas

    def coletar_temporadas_de_competicao(self, url_competicao: str) -> Tuple[List[str], str]:
        """Lógica de extração com sistema de fallback para temporadas."""
        self.logger.info(f"Coletando temporadas de: {url_competicao}")
        
        try:
            soup = fazer_requisicao(url_competicao)
            if not soup:
                self.logger.warning("Falha na requisição da página de competição")
                return [], "unknown"
            
            links = []
            tipo = "unknown"
            
            # Método 1: Procurar por links diretos de temporadas
            season_links = soup.find_all('a', href=True)
            for link in season_links:
                href = link.get('href')
                if href and any(keyword in href for keyword in ['/en/', 'stats', 'schedule']):
                    if not href.startswith('http'):
                        href = BASE_URL + href
                    links.append(href)
                    tipo = "season"
            
            # Método 2: Se não encontrou links diretos, tenta o método de tabela
            if not links:
                links = self.extrair_links_de_torneios_da_tabela(soup)
                if links:
                    tipo = "tournament"
            
            # Remove duplicatas e filtra links válidos
            links = list(set(links))
            links = [link for link in links if link and 'fbref.com' in link]
            
            self.logger.info(f"Encontrados {len(links)} links do tipo {tipo}")
            return links, tipo
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar temporadas de {url_competicao}: {e}")
            return [], "error"

    def salvar_competicao_no_banco(self, session: Session, competicao_data: Dict[str, str]) -> Optional[int]:
        """Salva uma competição no banco usando ORM e retorna o ID."""
        try:
            # Verificar se competição já existe
            competicao_existente = session.query(Competicao).filter_by(
                nome=competicao_data['nome'],
                contexto=competicao_data['contexto']
            ).first()
            
            if competicao_existente:
                self.logger.debug(f"Competição já existe: {competicao_data['nome']} ({competicao_data['contexto']})")
                return competicao_existente.id
            
            # Criar nova competição
            nova_competicao = Competicao(
                nome=competicao_data['nome'],
                url=competicao_data['url'],
                contexto=competicao_data['contexto'],
                ativa=True
            )
            
            session.add(nova_competicao)
            session.flush()  # Para obter o ID sem commit
            
            self.logger.info(f"Competição salva: {competicao_data['nome']} (ID: {nova_competicao.id})")
            return nova_competicao.id
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao salvar competição {competicao_data['nome']}: {e}")
            session.rollback()
            return None

    def salvar_links_no_banco(self, session: Session, competicao_id: int, links: List[str], tipo: str) -> int:
        """Salva links de temporadas no banco usando ORM."""
        links_salvos = 0
        
        try:
            for link in links:
                # Verificar se link já existe
                link_existente = session.query(LinkParaColeta).filter_by(
                    url=link,
                    competicao_id=competicao_id
                ).first()
                
                if link_existente:
                    self.logger.debug(f"Link já existe: {link}")
                    continue
                
                # Criar novo link
                novo_link = LinkParaColeta(
                    url=link,
                    competicao_id=competicao_id,
                    tipo=tipo,
                    status='pendente',
                    prioridade=1
                )
                
                session.add(novo_link)
                links_salvos += 1
            
            self.logger.info(f"Salvos {links_salvos} novos links para competição {competicao_id}")
            return links_salvos
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao salvar links: {e}")
            session.rollback()
            return 0

    def main(self, modo_teste: bool = False) -> Optional[Dict[str, int]]:
        """Orquestra a coleta de links e salva na fila de trabalho do banco de dados usando ORM."""
        self.logger.info("=== INICIANDO SCRIPT DE DESCOBERTA DE COMPETIÇÕES (ORM) ===")
        
        try:
            # Testar conexão com banco de dados
            if not db_manager.test_connection():
                self.logger.error("❌ Falha na conexão com banco de dados")
                return None
            
            self.logger.info("✅ Conexão com banco de dados estabelecida")
            
            # Coletar lista de competições
            self.logger.info("Coletando lista de competições...")
            lista_competicoes = self.coletar_competicoes()
            
            if not lista_competicoes:
                self.logger.error("Nenhuma competição encontrada")
                return {"competicoes_encontradas": 0, "links_coletados": 0}
            
            # Modo teste: processa apenas as primeiras 5 competições
            if modo_teste:
                lista_competicoes = lista_competicoes[:5]
                self.logger.info(f"MODO TESTE ATIVADO: Processando apenas as primeiras {len(lista_competicoes)} competições")
            
            total_links = 0
            competicoes_processadas = 0
            competicoes_com_erro = 0
            
            # Processa em lotes menores para melhor controle
            lote_size = 5 if modo_teste else 10
            total_competicoes = len(lista_competicoes)
            
            self.logger.info(f"Processando {total_competicoes} competições em lotes de {lote_size}")
            
            # Usar sessão de banco de dados
            with SessionLocal() as session:
                for lote_inicio in range(0, total_competicoes, lote_size):
                    lote_fim = min(lote_inicio + lote_size, total_competicoes)
                    lote_competicoes = lista_competicoes[lote_inicio:lote_fim]
                    
                    self.logger.info(f"\n=== PROCESSANDO LOTE {lote_inicio//lote_size + 1}/{(total_competicoes + lote_size - 1)//lote_size} ===")
                    self.logger.info(f"Competições {lote_inicio + 1} a {lote_fim} de {total_competicoes}")
                    
                    for i, comp in enumerate(lote_competicoes):
                        indice_global = lote_inicio + i + 1
                        self.logger.info(f"\n--- Processando Competição {indice_global}/{total_competicoes}: {comp['nome']} ({comp['contexto']}) ---")
                        
                        try:
                            # Salva competição e obtém ID
                            competicao_id = self.salvar_competicao_no_banco(session, comp)
                            if not competicao_id:
                                self.logger.error(f"Falha ao salvar competição: {comp['nome']}")
                                competicoes_com_erro += 1
                                continue
                            
                            # Coleta links de temporadas com timeout individual
                            links, tipo = self.coletar_temporadas_de_competicao(comp['url'])
                            self.logger.info(f"  -> Encontrados {len(links)} links do tipo {tipo}.")
                            
                            # Salva links no banco
                            links_salvos = self.salvar_links_no_banco(session, competicao_id, links, tipo)
                            
                            total_links += links_salvos
                            competicoes_processadas += 1
                            
                            # Commit a cada competição para não perder dados
                            session.commit()
                            
                        except Exception as e:
                            self.logger.error(f"Erro ao processar competição {comp['nome']}: {e}")
                            session.rollback()
                            competicoes_com_erro += 1
                            continue
                    
                    # Log de progresso do lote
                    self.logger.info(f"\n✅ Lote {lote_inicio//lote_size + 1} concluído:")
                    self.logger.info(f"  -> {competicoes_processadas} competições processadas até agora")
                    self.logger.info(f"  -> {competicoes_com_erro} competições com erro")
                    self.logger.info(f"  -> {total_links} links coletados até agora")
            
            self.logger.info(f"\n✅ Script 1 (Descoberta ORM) finalizado com sucesso!")
            self.logger.info(f"  -> {competicoes_processadas} competições processadas com sucesso")
            self.logger.info(f"  -> {competicoes_com_erro} competições com erro")
            self.logger.info(f"  -> {total_links} links de temporadas coletados")
            
            return {
                "competicoes_encontradas": len(lista_competicoes),
                "competicoes_processadas": competicoes_processadas,
                "competicoes_com_erro": competicoes_com_erro,
                "links_coletados": total_links
            }
            
        except Exception as e:
            self.logger.error(f"Erro crítico no script de descoberta ORM: {e}", exc_info=True)
            return None
            
        finally:
            # Chama fechar_driver para limpar recursos do Selenium se houver
            fechar_driver(None)

    def processar_partida_com_stats_avancadas(self, partida_id: int, match_url: str) -> bool:
        """
        Processa uma partida individual e extrai estatísticas avançadas.
        
        Args:
            partida_id: ID da partida no banco de dados
            match_url: URL da partida no FBRef
            
        Returns:
            bool: True se processou com sucesso, False caso contrário
        """
        self.logger.info(f"Processando estatísticas avançadas para partida {partida_id}: {match_url}")
        
        try:
            # Extrai estatísticas avançadas usando o novo módulo
            advanced_stats = extract_advanced_match_stats(match_url, headless=True)
            
            if not advanced_stats:
                self.logger.warning(f"Nenhuma estatística avançada encontrada para partida {partida_id}")
                return False
            
            # Salva as estatísticas no banco usando ORM
            with SessionLocal() as session:
                try:
                    # Busca a partida no banco
                    partida = session.query(Partida).filter_by(id=partida_id).first()
                    if not partida:
                        self.logger.error(f"Partida {partida_id} não encontrada no banco")
                        return False
                    
                    # Busca ou cria registro de estatísticas da partida
                    estatistica = session.query(EstatisticaPartida).filter_by(partida_id=partida_id).first()
                    if not estatistica:
                        estatistica = EstatisticaPartida(partida_id=partida_id)
                        session.add(estatistica)
                    
                    # Atualiza os campos de estatísticas avançadas
                    estatistica.xg_casa = advanced_stats.home_xg
                    estatistica.xg_visitante = advanced_stats.away_xg
                    estatistica.xa_casa = advanced_stats.home_xa
                    estatistica.xa_visitante = advanced_stats.away_xa
                    estatistica.formacao_casa = advanced_stats.home_formation
                    estatistica.formacao_visitante = advanced_stats.away_formation
                    
                    # Commit das alterações
                    session.commit()
                    
                    self.logger.info(f"Estatísticas avançadas salvas para partida {partida_id}:")
                    self.logger.info(f"  -> xG: {advanced_stats.home_team} {advanced_stats.home_xg} - {advanced_stats.away_xg} {advanced_stats.away_team}")
                    self.logger.info(f"  -> xA: {advanced_stats.home_xa} - {advanced_stats.away_xa}")
                    self.logger.info(f"  -> Formações: {advanced_stats.home_formation} vs {advanced_stats.away_formation}")
                    
                    return True
                    
                except SQLAlchemyError as e:
                    self.logger.error(f"Erro ao salvar estatísticas avançadas para partida {partida_id}: {e}")
                    session.rollback()
                    return False
                    
        except Exception as e:
            self.logger.error(f"Erro inesperado ao processar partida {partida_id}: {e}")
            logger.debug(traceback.format_exc())
            return False
            
    def processar_partidas_pendentes_com_stats_avancadas(self, limite: Optional[int] = None) -> Dict[str, int]:
        """Processa partidas pendentes e extrai estatísticas avançadas.
        
        Args:
            limite: Número máximo de partidas a processar (None para todas)
            
        Returns:
            Dicionário com estatísticas do processamento
        """
        self.logger.info("Iniciando processamento de partidas com estatísticas avançadas...")
        
        stats = {
            'partidas_processadas': 0,
            'partidas_com_sucesso': 0,
            'partidas_com_erro': 0,
            'partidas_sem_url': 0
        }
        
        try:
            with SessionLocal() as session:
                # Busca partidas que têm URL mas ainda não têm estatísticas avançadas
                query = session.query(Partida).filter(
                    Partida.url_fbref.isnot(None),
                    Partida.url_fbref != ''
                ).outerjoin(EstatisticaPartida).filter(
                    (EstatisticaPartida.xg_casa.is_(None)) |
                    (EstatisticaPartida.xg_visitante.is_(None))
                )
                
                if limite:
                    query = query.limit(limite)
                
                partidas = query.all()
                total_partidas = len(partidas)
                
                if not partidas:
                    self.logger.info("Nenhuma partida pendente encontrada para processamento de estatísticas avançadas")
                    return stats
                
                self.logger.info(f"Encontradas {total_partidas} partidas para processar")
                
                for i, partida in enumerate(partidas, 1):
                    self.logger.info(f"Processando partida {i}/{total_partidas}: {partida.id}")
                    
                    if not partida.url_fbref:
                        stats['partidas_sem_url'] += 1
                        continue
                    
                    sucesso = self.processar_partida_com_stats_avancadas(partida.id, partida.url_fbref)
                    
                    if sucesso:
                        stats['partidas_com_sucesso'] += 1
                    else:
                        stats['partidas_com_erro'] += 1
                    
                    stats['partidas_processadas'] += 1
                    
                    # Pequena pausa para evitar sobrecarga do servidor
                    import time
                    time.sleep(2)
                
                self.logger.info(f"Processamento concluído:")
                self.logger.info(f"  -> {stats['partidas_processadas']} partidas processadas")
                self.logger.info(f"  -> {stats['partidas_com_sucesso']} com sucesso")
                self.logger.info(f"  -> {stats['partidas_com_erro']} com erro")
                self.logger.info(f"  -> {stats['partidas_sem_url']} sem URL")
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Erro crítico no processamento de partidas: {e}")
            return stats

# Funções de compatibilidade para manter a interface existente
def coletar_competicoes() -> List[Dict[str, str]]:
    """Função de compatibilidade."""
    collector = FBRefCollectorORM()
    return collector.coletar_competicoes()

def main(modo_teste: bool = False) -> Optional[Dict[str, int]]:
    """Função principal de compatibilidade."""
    collector = FBRefCollectorORM()
    return collector.main(modo_teste)

def processar_partidas_com_estatisticas_avancadas(limite: Optional[int] = None) -> Dict[str, int]:
    """Função de conveniência para processar partidas com estatísticas avançadas."""
    collector = FBRefCollectorORM()
    return collector.processar_partidas_pendentes_com_stats_avancadas(limite)

if __name__ == "__main__":
    main()
