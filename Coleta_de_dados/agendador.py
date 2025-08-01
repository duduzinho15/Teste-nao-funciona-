import schedule 
import time
from apis import sofascore_scraper
from apis import thesportsdb_api
from utils.log_utils import registrar_log

def tarefa_sofascore():
    try:
        registrar_log("sofascore", "Iniciando coleta agendada...")
        sofascore_scraper.executar_coleta_sofascore()
        registrar_log("sofascore", "Coleta concluída com sucesso.")
    except Exception as e:
        registrar_log("sofascore", f"Erro durante a coleta agendada: {e}", tipo="ERRO")

def tarefa_thesportsdb():
    try:
        registrar_log("thesportsdb", "Iniciando coleta agendada...")
        thesportsdb_api.executar_coleta_thesportsdb()
        registrar_log("thesportsdb", "Coleta concluída com sucesso.")
    except Exception as e:
        registrar_log("thesportsdb", f"Erro durante a coleta agendada: {e}", tipo="ERRO")

# Agendar as tarefas para rodar a cada 6 horas
schedule.every(6).hours.do(tarefa_sofascore)
schedule.every(6).hours.do(tarefa_thesportsdb)

if __name__ == "__main__":
    registrar_log("agendador", "Agendador iniciado.")
    while True:
        schedule.run_pending()
        time.sleep(60)