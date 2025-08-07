import logging
import time
import sys
import os
import multiprocessing
import queue
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from contextlib import contextmanager
import traceback
import json
from datetime import datetime
# Configuração de paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# Importações dos módulos otimizados
from Banco_de_dados.criar_banco import criar_todas_as_tabelas
from Coleta_de_dados.apis.fbref.fbref_integrado import main as descobrir_links
from Coleta_de_dados.apis.fbref.coletar_dados_partidas import main as coletar_partidas
from Coleta_de_dados.apis.fbref.coletar_estatisticas_detalhadas import main as coletar_estatisticas
from Coleta_de_dados.apis.fbref.fbref_criar_tabela_rotulada import main as processar_dados
from Coleta_de_dados.apis.fbref.gerar_relatorio_final import main as gerar_relatorio
logger = logging.getLogger(__name__)

# Worker function for multiprocessing - must be at module level for Windows compatibility
def _timeout_worker(func_and_args_queue, result_queue):
    """Worker function for timeout execution - defined at module level for Windows pickling."""
    try:
        func, args, kwargs = func_and_args_queue.get()
        if args and kwargs:
            result = func(*args, **kwargs)
        elif args:
            result = func(*args)
        elif kwargs:
            result = func(**kwargs)
        else:
            result = func()
        result_queue.put(result)
    except Exception as e:
        result_queue.put(e)
@dataclass
class EtapaExecucao:
    """Classe para definir uma etapa da pipeline."""
    nome: str
    descricao: str
    funcao: Callable
    obrigatoria: bool = True
    timeout: Optional[int] = None
@dataclass
class ResultadoEtapa:
    """Classe para armazenar o resultado de uma etapa."""
    nome: str
    sucesso: bool
    tempo_execucao: float
    erro: Optional[str] = None
    dados_retorno: Optional[Any] = None
@dataclass
class EstatisticasPipeline:
    """Classe para estatísticas gerais da pipeline."""
    tempo_total: float = 0.0
    etapas_executadas: int = 0
    etapas_com_sucesso: int = 0
    etapas_com_erro: int = 0
    dados_coletados: Dict[str, int] = None
    def __post_init__(self):
        if self.dados_coletados is None:
            self.dados_coletados = {}
class OrquestradorColeta:
    """Classe principal para orquestração da pipeline de coleta."""
    
    def __init__(self, config_arquivo: Optional[str] = None):
        self.config = self._carregar_configuracao(config_arquivo)
        self.resultados_etapas = []
        self.stats = EstatisticasPipeline()
        # Definição das etapas da pipeline
        self.etapas = [
            EtapaExecucao(
                nome="preparacao_banco",
                descricao="Preparação do Banco de Dados",
                funcao=self._executar_preparacao_banco,
                timeout=300  # 5 minutos
            ),
            EtapaExecucao(
                nome="descoberta_links",
                descricao="Descoberta de Competições e Temporadas",
                funcao=self._executar_descoberta_links,
                timeout=900  # 15 minutos (reduzido de 30 minutos)
            ),
            EtapaExecucao(
                nome="verificacao_extracao",
                descricao="Verificação da Completude da Extração",
                funcao=self._executar_verificacao_extracao,
                timeout=900  # 15 minutos
            ),
            EtapaExecucao(
                nome="coleta_partidas",
                descricao="Coleta de Dados de Partidas",
                funcao=self._executar_coleta_partidas,
                timeout=3600  # 1 hora
            ),
            EtapaExecucao(
                nome="coleta_estatisticas",
                descricao="Coleta de Estatísticas Detalhadas",
                funcao=self._executar_coleta_estatisticas,
                timeout=7200  # 2 horas
            ),
            EtapaExecucao(
                nome="coleta_clubes",
                descricao="Coleta de Dados de Clubes",
                funcao=self._executar_coleta_clubes,
                timeout=3600  # 1 hora
            ),
            EtapaExecucao(
                nome="coleta_jogadores",
                descricao="Coleta de Dados de Jogadores",
                funcao=self._executar_coleta_jogadores,
                timeout=3600  # 1 hora
            ),
            EtapaExecucao(
                nome="processamento_dados",
                descricao="Processamento e Rotulação dos Dados para IA",
                funcao=self._executar_processamento_dados,
                timeout=600  # 10 minutos
            ),
            EtapaExecucao(
                nome="geracao_relatorio",
                descricao="Geração do Relatório Final de Coleta",
                funcao=self._executar_geracao_relatorio,
                obrigatoria=False,  # Não crítica
                timeout=300  # 5 minutos
            )
        ]
    def _carregar_configuracao(self, config_arquivo: Optional[str]) -> Dict[str, Any]:
        """Carrega configurações da pipeline."""
        config_padrao = {
            'continuar_em_erro': True,  # ✅ Continuar mesmo com erros não críticos
            'salvar_logs_detalhados': True,
            'backup_antes_execucao': True,
            'timeout_global': 14400,  # 4 horas
            'intervalo_checkpoint': 300,  # 5 minutos
            'modo_teste': False,  # ✅ Modo teste desabilitado por padrão
            'limite_competicoes': None,  # ✅ Sem limite por padrão
        }
        if config_arquivo and os.path.exists(config_arquivo):
            try:
                with open(config_arquivo, 'r', encoding='utf-8') as f:
                    config_carregada = json.load(f)
                config_padrao.update(config_carregada)
            except Exception as e:
                logger.warning(f"Erro ao carregar configuração: {e}. Usando configuração padrão.")
        return config_padrao
    @contextmanager
    def _timeout_context(self, seconds: Optional[int]):
        """Context manager para timeout de execução que funciona no Windows."""
        if seconds is None:
            yield
            return
            
        import threading
        import signal
        
        # Verifica se estamos no Windows
        if os.name == 'nt':  # Windows
            # Implementação para Windows usando threading
            result = {'value': None, 'exception': None}
            
            def target():
                try:
                    result['value'] = yield
                except Exception as e:
                    result['exception'] = e
            
            def timeout_handler():
                result['exception'] = TimeoutError(f"Operação excedeu timeout de {seconds} segundos")
            
            timer = threading.Timer(seconds, timeout_handler)
            timer.start()
            
            try:
                yield
                timer.cancel()
                
                if result['exception']:
                    raise result['exception']
                    
            except Exception as e:
                timer.cancel()
                raise e
                
        else:
            # Implementação para Unix/Linux usando signal
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Operação excedeu timeout de {seconds} segundos")
            
            if hasattr(signal, 'SIGALRM'):
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)
                try:
                    yield
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
            else:
                logger.warning("Timeout não suportado neste sistema. Executando sem timeout.")
                yield
    def _run_with_timeout(self, func, timeout, *args, **kwargs):
        """Executa função com timeout universal"""
        # Use queues for communication with the worker process
        func_queue = multiprocessing.Queue()
        result_queue = multiprocessing.Queue()
        
        # Put function and arguments in the queue
        func_queue.put((func, args, kwargs))
        
        # Start worker process
        p = multiprocessing.Process(target=_timeout_worker, args=(func_queue, result_queue))
        p.start()
        p.join(timeout)
        
        if p.is_alive():
            p.terminate()
            p.join()
            raise TimeoutError(f"Timeout após {timeout}s")
        
        # Get result from queue
        if not result_queue.empty():
            result = result_queue.get()
            if isinstance(result, Exception):
                raise result
            return result
        else:
            raise RuntimeError("Processo terminou sem retornar resultado")
    def _executar_etapa_com_tratamento(self, etapa: EtapaExecucao) -> ResultadoEtapa:
        """Executa uma etapa individual com tratamento completo de erros."""
        logger.info(f"\n--- [ETAPA {self.stats.etapas_executadas + 1} de {len(self.etapas)}] Executando: {etapa.descricao} ---")
        start_time = time.time()
        resultado = ResultadoEtapa(nome=etapa.nome, sucesso=False, tempo_execucao=0.0)
        try:
            with self._timeout_context(etapa.timeout):
                # Alterado para usar _run_with_timeout
                dados_retorno = self._run_with_timeout(etapa.funcao, etapa.timeout)
                resultado.sucesso = True
                resultado.dados_retorno = dados_retorno
            logger.info(f"--- [ETAPA {self.stats.etapas_executadas + 1}] Finalizada com sucesso! ---")
        except TimeoutError as e:
            resultado.erro = f"Timeout: {str(e)}"
            logger.error(f"--- [ETAPA {self.stats.etapas_executadas + 1}] TIMEOUT: {e} ---")
        except Exception as e:
            resultado.erro = str(e)
            logger.error(f"--- [ETAPA {self.stats.etapas_executadas + 1}] ERRO: {e} ---")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(traceback.format_exc())
        finally:
            resultado.tempo_execucao = time.time() - start_time
            self.stats.etapas_executadas += 1
            if resultado.sucesso:
                self.stats.etapas_com_sucesso += 1
            else:
                self.stats.etapas_com_erro += 1
        return resultado
    def _deve_continuar_execucao(self, resultado: ResultadoEtapa, etapa: EtapaExecucao) -> bool:
        """Determina se a pipeline deve continuar após uma etapa."""
        if resultado.sucesso:
            logger.info(f"✅ Etapa '{etapa.nome}' executada com sucesso - continuando pipeline")
            return True
        
        if not etapa.obrigatoria:
            logger.warning(f"⚠️ Etapa não obrigatória '{etapa.nome}' falhou - continuando pipeline")
            logger.info(f"📋 Detalhes do erro: {resultado.erro}")
            return True
        
        if self.config.get('continuar_em_erro', False):
            logger.warning(f"🔄 Etapa obrigatória '{etapa.nome}' falhou - continuando por configuração")
            logger.warning(f"📋 Detalhes do erro: {resultado.erro}")
            return True
        
        logger.error(f"🛑 Etapa obrigatória '{etapa.nome}' falhou - interrompendo pipeline")
        logger.error(f"📋 Detalhes do erro: {resultado.erro}")
        return False
    def _salvar_checkpoint(self) -> None:
        """Salva um checkpoint do estado atual da pipeline."""
        try:
            checkpoint_data = {
                'timestamp': datetime.now().isoformat(),
                'etapas_executadas': self.stats.etapas_executadas,
                'etapas_com_sucesso': self.stats.etapas_com_sucesso,
                'resultados': [
                    {
                        'nome': r.nome,
                        'sucesso': r.sucesso,
                        'tempo_execucao': r.tempo_execucao,
                        'erro': r.erro
                    }
                    for r in self.resultados_etapas
                ]
            }
            checkpoint_file = os.path.join(PROJECT_ROOT, 'checkpoint_pipeline.json')
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Checkpoint salvo em: {checkpoint_file}")
        except Exception as e:
            logger.warning(f"Erro ao salvar checkpoint: {e}")
    def _gerar_relatorio_execucao(self) -> None:
        """Gera relatório detalhado da execução da pipeline."""
        logger.info("\n" + "="*80)
        logger.info("📊 RELATÓRIO FINAL DA PIPELINE")
        logger.info("="*80)
        logger.info(f"⏱️  Tempo total de execução: {time.strftime('%H:%M:%S', time.gmtime(self.stats.tempo_total))}")
        logger.info(f"📈 Etapas executadas: {self.stats.etapas_executadas}/{len(self.etapas)}")
        logger.info(f"✅ Etapas com sucesso: {self.stats.etapas_com_sucesso}")
        logger.info(f"❌ Etapas com erro: {self.stats.etapas_com_erro}")
        logger.info("\n📋 DETALHES POR ETAPA:")
        for resultado in self.resultados_etapas:
            status = "✅ SUCESSO" if resultado.sucesso else "❌ ERRO"
            tempo_str = time.strftime('%H:%M:%S', time.gmtime(resultado.tempo_execucao))
            logger.info(f"  {status} | {resultado.nome:<20} | {tempo_str}")
            if resultado.erro:
                logger.info(f"    └─ Erro: {resultado.erro}")
        # Estatísticas de dados coletados
        if self.stats.dados_coletados:
            logger.info("\n📊 DADOS COLETADOS:")
            for chave, valor in self.stats.dados_coletados.items():
                logger.info(f"  {chave}: {valor:,}")
        logger.info("="*80)
    # Métodos wrapper para as etapas individuais
    def _executar_preparacao_banco(self):
        """Wrapper para preparação do banco de dados."""
        logger.info("Iniciando preparação do banco de dados...")
        return criar_todas_as_tabelas()
    def _executar_descoberta_links(self):
        """Wrapper para descoberta de links com controle de modo teste."""
        modo_teste = self.config.get('modo_teste', False)
        logger.info(f"Iniciando descoberta de competições e temporadas (modo_teste={modo_teste})")
        if modo_teste:
            logger.info("🧪 MODO TESTE ATIVADO - Processamento limitado")
        from .fbref_integrado import main
        return main(modo_teste=modo_teste)
    def _executar_coleta_partidas(self):
        """Wrapper para coleta de partidas."""
        logger.info("Iniciando coleta de dados de partidas...")
        resultado = coletar_partidas()
        if isinstance(resultado, dict):
            self.stats.dados_coletados.update({
                'partidas_coletadas': resultado.get('partidas_encontradas', 0),
                'links_processados': resultado.get('links_processados', 0)
            })
        return resultado
    def _executar_coleta_estatisticas(self):
        """Wrapper para coleta de estatísticas."""
        logger.info("Iniciando coleta de estatísticas detalhadas...")
        resultado = coletar_estatisticas()
        if isinstance(resultado, dict):
            self.stats.dados_coletados.update({
                'jogadores_processados': resultado.get('jogadores_processados', 0),
                'partidas_com_stats': resultado.get('partidas_processadas', 0)
            })
        return resultado
    def _executar_processamento_dados(self):
        """Wrapper para processamento de dados."""
        logger.info("Iniciando processamento e rotulação dos dados...")
        return processar_dados()
    def _executar_verificacao_extracao(self):
        """Wrapper para verificação da completude da extração."""
        logger.info("Iniciando verificação da completude da extração...")
        from .verificar_extracao import VerificadorExtracao
        verificador = VerificadorExtracao()
        return verificador.executar_verificacao_completa()

    def _executar_coleta_clubes(self):
        """Wrapper para coleta de clubes."""
        logger.info("Iniciando coleta de dados de clubes...")
        from .coletar_clubes import ColetorClubes
        coletor = ColetorClubes()
        resultado = coletor.executar_coleta_completa()
        if isinstance(resultado, dict):
            self.stats.dados_coletados.update({
                'paises_processados': resultado.get('paises_processados', 0),
                'clubes_encontrados': resultado.get('clubes_encontrados', 0),
                'clubes_masculino': resultado.get('clubes_masculino', 0),
                'clubes_feminino': resultado.get('clubes_feminino', 0)
            })
        return resultado

    def _executar_coleta_jogadores(self):
        """Wrapper para coleta de jogadores."""
        logger.info("Iniciando coleta de dados de jogadores...")
        from .coletar_jogadores import ColetorJogadores
        coletor = ColetorJogadores()
        resultado = coletor.executar_coleta_completa()
        if isinstance(resultado, dict):
            self.stats.dados_coletados.update({
                'paises_jogadores_processados': resultado.get('paises_processados', 0),
                'jogadores_encontrados': resultado.get('jogadores_encontrados', 0),
                'jogadores_com_stats': resultado.get('jogadores_com_stats', 0)
            })
        return resultado

    def _executar_geracao_relatorio(self):
        """Wrapper para geração de relatório."""
        logger.info("Iniciando geração do relatório final...")
        return gerar_relatorio()
    def executar_pipeline_completa(self) -> bool:
        """
        Executa todos os scripts da pipeline de dados em sequência.
        Returns:
            bool: True se a pipeline foi executada com sucesso
        """
        start_time = time.time()
        pipeline_sucesso = True
        logger.info("🚀🚀🚀 INICIANDO A PIPELINE COMPLETA DE DADOS DO FBREF 🚀🚀🚀")
        logger.info(f"Configuração: {self.config}")
        try:
            # Executa cada etapa
            for etapa in self.etapas:
                # Checkpoint periódico
                if time.time() - start_time > self.config.get('intervalo_checkpoint', 300):
                    self._salvar_checkpoint()
                # Executa a etapa
                resultado = self._executar_etapa_com_tratamento(etapa)
                self.resultados_etapas.append(resultado)
                # Verifica se deve continuar
                if not self._deve_continuar_execucao(resultado, etapa):
                    pipeline_sucesso = False
                    break
            # Checkpoint final
            self._salvar_checkpoint()
        except KeyboardInterrupt:
            logger.warning("🛑 Pipeline interrompida pelo usuário (Ctrl+C)")
            pipeline_sucesso = False
        except Exception as e:
            logger.critical(f"🚨🚨🚨 ERRO CRÍTICO NA PIPELINE! 🚨🚨🚨", exc_info=True)
            pipeline_sucesso = False
        finally:
            # Calcular estatísticas finais
            self.stats.tempo_total = time.time() - start_time
            # Gerar relatório final
            self._gerar_relatorio_execucao()
            # Status final
            if pipeline_sucesso and self.stats.etapas_com_erro == 0:
                logger.info("✅✅✅ PIPELINE COMPLETA FINALIZADA COM SUCESSO! ✅✅✅")
            elif pipeline_sucesso:
                logger.warning("⚠️⚠️⚠️ PIPELINE FINALIZADA COM AVISOS ⚠️⚠️⚠️")
            else:
                logger.error("❌❌❌ PIPELINE FINALIZADA COM ERROS ❌❌❌")
        return pipeline_sucesso
    def executar_etapa_individual(self, nome_etapa: str) -> bool:
        """
        Executa uma etapa individual da pipeline.
        Args:
            nome_etapa: Nome da etapa a ser executada
        Returns:
            bool: True se a etapa foi executada com sucesso
        """
        etapa = next((e for e in self.etapas if e.nome == nome_etapa), None)
        if not etapa:
            logger.error(f"Etapa '{nome_etapa}' não encontrada.")
            return False
        logger.info(f"🚀 Executando etapa individual: {etapa.descricao}")
        resultado = self._executar_etapa_com_tratamento(etapa)
        self.resultados_etapas.append(resultado)
        return resultado.sucesso
    def listar_etapas(self) -> None:
        """Lista todas as etapas disponíveis."""
        logger.info("📋 ETAPAS DISPONÍVEIS NA PIPELINE:")
        for i, etapa in enumerate(self.etapas, 1):
            obrigatoria = "OBRIGATÓRIA" if etapa.obrigatoria else "OPCIONAL"
            timeout_info = f"(timeout: {etapa.timeout}s)" if etapa.timeout else ""
            logger.info(f"  {i}. {etapa.nome} - {etapa.descricao} [{obrigatoria}] {timeout_info}")
def executar_pipeline_completa(config_arquivo: Optional[str] = None) -> bool:
    """
    Função utilitária para executar a pipeline completa.
    Args:
        config_arquivo: Caminho para arquivo de configuração opcional
    Returns:
        bool: True se executou com sucesso
    """
    orquestrador = OrquestradorColeta(config_arquivo)
    return orquestrador.executar_pipeline_completa()
def main():
    """Função principal para execução standalone."""
    import argparse
    parser = argparse.ArgumentParser(description='Orquestrador da Pipeline FBRef')
    parser.add_argument('--config', help='Arquivo de configuração JSON')
    parser.add_argument('--etapa', help='Executar apenas uma etapa específica')
    parser.add_argument('--listar', action='store_true', help='Listar etapas disponíveis')
    parser.add_argument('--debug', action='store_true', help='Ativar logging debug')
    args = parser.parse_args()
    # Configurar logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    # Criar orquestrador
    orquestrador = OrquestradorColeta(args.config)
    # Executar ação solicitada
    if args.listar:
        orquestrador.listar_etapas()
        return True
    elif args.etapa:
        return orquestrador.executar_etapa_individual(args.etapa)
    else:
        return orquestrador.executar_pipeline_completa()
if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)