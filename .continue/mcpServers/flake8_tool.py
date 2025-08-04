import subprocess

from mcp.server import FastMCP


# Inicializa o servidor MCP com um nome único
mcp = FastMCP("flake8_linter")


@mcp.tool()
async def run_flake8(filepath: str = ".") -> str:
    """
    Executa o linter flake8 em um arquivo específico ou em todo o projeto.
    Args:
        filepath: O caminho para o arquivo ou diretório Python a ser analisado. O padrão é o diretório atual '.'.
    Returns:
        Uma string contendo a saída do flake8, ou uma mensagem de sucesso se nenhum problema for encontrado.
    """
    try:
        # Assume que o executável do python do ambiente virtual está no PATH
        # e que o flake8 foi instalado nele.
        command = ["flake8", filepath]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if result.stdout:
            return f"O Flake8 encontrou os seguintes problemas:\n{result.stdout}"
        if result.stderr:
            return f"O Flake8 encontrou um erro durante a execução:\n{result.stderr}"
        
        return "O Flake8 foi executado com sucesso. Nenhum problema encontrado."
    except FileNotFoundError:
        return "Erro: comando 'flake8' não encontrado. Por favor, garanta que ele está instalado e no seu PATH."
    except Exception as e:
        return f"Um erro inesperado ocorreu: {e}"


if __name__ == "__main__":
    # Inicia o servidor para comunicar via stdio
    mcp.run(transport='stdio')
