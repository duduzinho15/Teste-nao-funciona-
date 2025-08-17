"""Scheduler for periodic data collection tasks.

This module uses APScheduler's :class:`BlockingScheduler` to run
data collection jobs at regular intervals. It replaces the previous
implementation based on the ``schedule`` library and a manual loop.
"""

import logging
from apscheduler.schedulers.blocking import BlockingScheduler

from apis.news.collector import coletar_noticias_para_todos_clubes
from apis.social.collector import coletar_dados_para_todos_clubes


logger = logging.getLogger(__name__)


def executar_coleta_noticias() -> None:
    """Wrapper para coleta de notícias de clubes."""
    logger.info("Iniciando coleta de notícias")
    try:
        coletar_noticias_para_todos_clubes()
        logger.info("Coleta de notícias concluída com sucesso")
    except Exception as exc:  # pragma: no cover - log for operational visibility
        logger.exception("Falha na coleta de notícias: %s", exc)


def executar_coleta_social() -> None:
    """Wrapper para coleta de dados de redes sociais."""
    logger.info("Iniciando coleta de redes sociais")
    try:
        coletar_dados_para_todos_clubes()
        logger.info("Coleta de redes sociais concluída com sucesso")
    except Exception as exc:  # pragma: no cover - log for operational visibility
        logger.exception("Falha na coleta de redes sociais: %s", exc)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(executar_coleta_noticias, "interval", hours=6)
    scheduler.add_job(executar_coleta_social, "interval", hours=6)

    try:
        logger.info("Agendador iniciado")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):  # pragma: no cover - runtime control
        logger.info("Agendador finalizado")

