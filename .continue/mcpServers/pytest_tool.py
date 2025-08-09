#.continue/mcpServers/pytest_tool.py
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pytest_runner")

@mcp.tool()
async def run_pytest(test_path: str = "tests/") -> str:
    """
    Executa o pytest em um arquivo de teste, diretório ou com um marcador específico.
    Args:
        test_path: O caminho para o arquivo/diretório de teste ou um nó de teste específico (ex: 'tests/test_routes.py::test_home_page'). O padrão é 'tests/'.
    Returns:
        Uma string contendo o resumo da saída do pytest.
    """
    try:
        # Usa argumentos para uma saída concisa
        command = ["pytest", "-q", "--tb=short", test_path]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        # Combina stdout e stderr para capturar toda a saída
        output = result.stdout + result.stderr
        return f"Execução do Pytest concluída.\nSaída:\n{output}"
    except Exception as e:
        return f"Um erro inesperado ocorreu ao executar o pytest: {e}"

if __name__ == "__main__":
    mcp.run(transport='stdio')