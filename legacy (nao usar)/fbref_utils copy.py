import re
from bs4 import BeautifulSoup
import requests

def obter_temporadas_disponiveis(url_competicao):
    response = requests.get(url_competicao)
    soup = BeautifulSoup(response.text, "html.parser")
    temporadas = []

    for link in soup.find_all("a", href=True):
        if "/en/comps/" in link["href"] and "Schedule" in link.text:
            temporadas.append({
                "nome": link.text.strip(),
                "url": f"https://fbref.com{link['href']}"
            })
    return temporadas

def obter_partidas_por_temporada(nome_competicao, temporada):
    print(f"\n🔗 Buscando partidas de {nome_competicao} - {temporada}...")

    COMPETICOES = {
        "Premier League": "9",
        # Adicione outras competições conforme necessário
    }

    comp_id = COMPETICOES.get(nome_competicao)
    if not comp_id:
        print(f"❌ Competição '{nome_competicao}' não mapeada.")
        return []

    nome_formatado = nome_competicao.replace(" ", "-")
    url = f"https://fbref.com/en/comps/{comp_id}/schedule/{temporada}-{nome_formatado}-Scores-and-Fixtures"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Erro ao acessar a página de partidas: {url}")
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/en/matches/"):
                full_url = f"https://fbref.com{href}"
                if full_url not in links:
                    links.append(full_url)

        print(f"🔗 {len(links)} links de partidas encontrados na temporada.")
        return links
    except Exception as e:
        print(f"❌ Erro ao processar a temporada: {e}")
        return []

def extrair_titulo_tabela(tabela_html):

    """
    Extrai o título da tabela. Tenta o <caption>, depois o id da tabela.
    """
    try:
        soup = BeautifulSoup(tabela_html, "html.parser")

        # 1. Primeiro tenta o <caption>
        caption = soup.find("caption")
        if caption:
            return caption.get_text(strip=True)

        # 2. Se não houver caption, tenta pegar o atributo id da <table>
        table = soup.find("table")
        if table and table.has_attr("id"):
            return f"{table['id']}Table"


    except Exception as e:
        print(f"⚠️ Erro ao extrair título: {e}")

    return "tabela_sem_titulo_id_desconhecido"

def identificar_tipo_tabela(titulo):
    if not titulo:
        return "tabela_desconhecida"

    titulo_original = titulo  # Salvar o original para debugging, se necessário
    titulo = titulo.lower().replace(" ", "").replace("\n", "").replace("-", "").replace("’", "").replace("'", "")

    padroes = {
        # Categorias gerais (existentes)
        "matchlog": "estatisticas_partidas",
        "shooting": "chutes",
        "keeper": "goleiros",
        "goalkeeperstatstable": "goleiros",
        "goalkeeping": "goleiros",
        "goalkeepingadv": "goleiros_avancado",
        "passing": "passes",
        "defense": "defesa",
        "possession": "posse",
        "miscellaneous": "estatisticas_misc",
        "passingtypes": "tipos_passes",
        "gca": "construcao_gols",
        "playingtime": "tempo_jogo",
        "teamstats": "estatisticas_times",
        "standard": "estatisticas_padrao",
        "scoresandfixtures": "tabela_jogos",
        "standings": "classificacao",
        "lineups": "escalacoes",
        "shootingagainst": "chutes_contra",
        "keeperagainst": "goleiros_contra",
        "opponentkeeper": "goleiros_oponente",

        # Padrões novos identificados (adicionados)
        "playerstatstable": "estatisticas_jogador",
        "shots": "chutes",
        "premierleaguetable": "classificacao",
        "ligaprofesionalargentinatable": "classificacao",
        "serieatable": "classificacao",
        "ligue1table": "classificacao",
        "laligatable": "classificacao",
        "eredivisietable": "classificacao",
        "bundesligatable": "classificacao",
        "championshiptable": "classificacao",
        "ligue2table": "classificacao",
        "superligtable": "classificacao",
        "brserieatable": "classificacao",
        "brseriebtable": "classificacao",
        "table": "classificacao",  # fallback genérico para qualquer "XTable"
    }

    for chave, tipo in padroes.items():
        if chave in titulo:
            return tipo
        
    return "tabela_desconhecida"

def identificar_tipo_por_conteudo(texto):
    """
    Detecta tipo da tabela com base no conteúdo visível, útil quando não há caption nem id.
    """
    texto = texto.lower()

    if any(palavra in texto for palavra in ["(4-2-3-1)", "(3-5-2)", "(4-3-3)", "(5-4-1)"]):
        return "escalacoes"
    if "possession" in texto and "shots" in texto:
        return "estatisticas_times"
    if "saves" in texto and "shots on target" in texto:
        return "estatisticas_times"

    return "tabela_desconhecida"