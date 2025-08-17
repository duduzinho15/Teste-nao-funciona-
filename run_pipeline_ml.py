"""Executa pipeline completo de Machine Learning.

Etapas:
1. Análise de sentimento dos textos.
2. Treinamento do modelo de previsão de resultados.
3. Geração de novas recomendações de apostas.
"""

import logging

from Coleta_de_dados.analise.sentimento import analisar_sentimento_textos
from Coleta_de_dados.ml.treinamento import treinar_modelo_resultado_final
from Coleta_de_dados.ml.gerar_recomendacoes import gerar_novas_recomendacoes

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def executar_pipeline_completo() -> None:
    """Executa todas as etapas do pipeline de ML com logs e tratamento de erros."""
    logger.info("Iniciando pipeline completo de Machine Learning")

    try:
        logger.info("Analisando sentimento dos textos...")
        analisar_sentimento_textos()
        logger.info("Análise de sentimento concluída com sucesso")
    except Exception as exc:
        logger.exception("Falha na análise de sentimento: %s", exc)
        return

    try:
        logger.info("Treinando modelo de resultado final...")
        treinar_modelo_resultado_final()
        logger.info("Treinamento do modelo concluído com sucesso")
    except Exception as exc:
        logger.exception("Falha no treinamento do modelo: %s", exc)
        return

    try:
        logger.info("Gerando novas recomendações...")
        gerar_novas_recomendacoes()
        logger.info("Geração de recomendações concluída com sucesso")
    except Exception as exc:
        logger.exception("Falha na geração de recomendações: %s", exc)
        return

    logger.info("Pipeline de Machine Learning finalizado com sucesso")


if __name__ == "__main__":
    executar_pipeline_completo()
