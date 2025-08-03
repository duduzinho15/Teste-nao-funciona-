#!/usr/bin/env python3
"""
Teste simplificado para parsing de comentarios HTML (sem emojis para Windows).
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def testar_parsing_comentarios():
    """Testa se o parsing de comentarios HTML funciona."""
    print("TESTE: Parsing de conteudo em comentarios HTML")
    print("=" * 50)
    
    try:
        from bs4 import BeautifulSoup
        from Coleta_de_dados.apis.fbref.fbref_utils import extrair_conteudo_comentarios_html
        
        # HTML de teste com tabela em comentario
        html_teste = """
        <html>
        <body>
            <h1>Teste</h1>
            <!-- 
            <table id="stats">
                <tr><td>Player</td><td>Goals</td></tr>
                <tr><td>Messi</td><td>30</td></tr>
            </table>
            -->
            <p>Fim</p>
        </body>
        </html>
        """
        
        soup_original = BeautifulSoup(html_teste, 'lxml')
        print(f"Tabelas originais: {len(soup_original.find_all('table'))}")
        
        # Processar comentarios
        soup_processado = extrair_conteudo_comentarios_html(soup_original)
        tabelas_processadas = soup_processado.find_all('table')
        print(f"Tabelas apos processamento: {len(tabelas_processadas)}")
        
        # Verificar se encontrou a tabela
        if len(tabelas_processadas) > 0:
            stats_table = soup_processado.find('table', id='stats')
            if stats_table:
                print("SUCESSO: Tabela 'stats' encontrada!")
                rows = stats_table.find_all('tr')
                print(f"Linhas na tabela: {len(rows)}")
                return True
            else:
                print("FALHA: Tabela 'stats' nao encontrada")
                return False
        else:
            print("FALHA: Nenhuma tabela encontrada")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Funcao principal."""
    print("INICIANDO TESTE DE PARSING DE COMENTARIOS")
    print("=" * 60)
    
    sucesso = testar_parsing_comentarios()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("RESULTADO: TESTE PASSOU!")
        return True
    else:
        print("RESULTADO: TESTE FALHOU!")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
