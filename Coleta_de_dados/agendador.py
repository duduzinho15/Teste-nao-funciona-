"""Agendador de coletas e pipeline ML."""

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

from apis import sofascore_scraper
from apis import thesportsdb_api
from utils.log_utils import registrar_log


scheduler = BlockingScheduler()


def tarefa_sofascore() -> None:
    """Executa a coleta agendada do Sofascore."""
    try:
        registrar_log("sofascore", "Iniciando coleta agendada...")
        sofascore_scraper.executar_coleta_sofascore()
        registrar_log("sofascore", "Coleta concluída com sucesso.")
    except Exception as e:  # pragma: no cover - log de erro
        registrar_log("sofascore", f"Erro durante a coleta agendada: {e}", tipo="ERRO")


def tarefa_thesportsdb() -> None:
    """Executa a coleta agendada do TheSportsDB."""
    try:
        registrar_log("thesportsdb", "Iniciando coleta agendada...")
        thesportsdb_api.executar_coleta_thesportsdb()
        registrar_log("thesportsdb", "Coleta concluída com sucesso.")
    except Exception as e:  # pragma: no cover - log de erro
        registrar_log("thesportsdb", f"Erro durante a coleta agendada: {e}", tipo="ERRO")


def executar_pipeline_diario() -> None:
    """Executa o pipeline diário de machine learning."""
    try:
        registrar_log("pipeline_ml", "Iniciando pipeline diário...")
        try:
            from run_pipeline_ml import executar_pipeline_completo

            executar_pipeline_completo()
        except Exception:
            subprocess.run(["python", "run_pipeline_ml.py"], check=True)
        registrar_log("pipeline_ml", "Pipeline diário concluído com sucesso.")
    except Exception as e:  # pragma: no cover - log de erro
        registrar_log("pipeline_ml", f"Erro durante execução do pipeline: {e}", tipo="ERRO")


def log_job_exception(event) -> None:
    """Registra exceções do scheduler."""
    if event.exception:
        registrar_log("scheduler", f"Erro no job {event.job_id}: {event.exception}", tipo="ERRO")


scheduler.add_listener(log_job_exception, EVENT_JOB_ERROR)

# Jobs existentes de coleta
scheduler.add_job(tarefa_sofascore, "interval", hours=6)
scheduler.add_job(tarefa_thesportsdb, "interval", hours=6)

# Novo job do pipeline ML diário
scheduler.add_job(executar_pipeline_diario, "cron", hour=3)


if __name__ == "__main__":
    registrar_log("agendador", "Agendador iniciado.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):  # pragma: no cover
        registrar_log("agendador", "Agendador finalizado.")

