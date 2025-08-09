"""
Script para verificar se a tabela noticias_clubes foi criada corretamente.
"""
import logging
from sqlalchemy import inspect
from Coleta_de_dados.database.config import db_manager

def print_header(text):
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, '='))
    print("=" * 80 + "\n")

def print_section(text):
    print(f"\n{' ' + text + ' ':-^80}\n")

def verificar_tabela():
    """Verifica se a tabela noticias_clubes existe no banco de dados."""
    session = None
    try:
        print_header("🔍 VERIFICAÇÃO DA TABELA 'noticias_clubes'")
        
        # Obter uma sessão do banco de dados
        session = db_manager.get_session()
        
        # Criar um inspetor para examinar o banco de dados
        inspector = inspect(session.get_bind())
        
        # Verificar se a tabela existe
        tabelas = inspector.get_table_names()
        tabela_existe = 'noticias_clubes' in tabelas
        
        print_section("TABELAS NO BANCO DE DADOS")
        for tabela in sorted(tabelas):
            print(f"- {tabela}")
        
        if not tabela_existe:
            print("\n❌ ERRO: Tabela 'noticias_clubes' NÃO encontrada no banco de dados!")
            return False
        
        print("\n✅ Tabela 'noticias_clubes' encontrada com sucesso!")
        
        # Obter detalhes das colunas
        print_section("COLUNAS DA TABELA 'noticias_clubes'")
        colunas = inspector.get_columns('noticias_clubes')
        print(f"{'Nome':<20} {'Tipo':<30} {'Nulo?'}  {'Default'}")
        print("-" * 80)
        for coluna in colunas:
            default = str(coluna.get('default', ''))[:30]
            print(f"{coluna['name']:<20} {str(coluna['type']):<30} {'Sim' if coluna['nullable'] else 'Não'}   {default}")
        
        # Verificar índices
        print_section("ÍNDICES DA TABELA 'noticias_clubes'")
        indices = inspector.get_indexes('noticias_clubes')
        if indices:
            print(f"{'Nome':<30} {'Colunas':<30} {'Único?'}")
            print("-" * 80)
            for indice in indices:
                print(f"{indice['name']:<30} {', '.join(indice['column_names']):<30} {'Sim' if indice.get('unique', False) else 'Não'}")
        else:
            print("Nenhum índice encontrado além da chave primária.")
        
        # Verificar chaves estrangeiras
        print_section("CHAVES ESTRANGEIRAS DA TABELA 'noticias_clubes'")
        fks = inspector.get_foreign_keys('noticias_clubes')
        if fks:
            print(f"{'Coluna':<20} {'Tabela Referenciada':<30} {'Coluna Referenciada'}")
            print("-" * 80)
            for fk in fks:
                print(f"{', '.join(fk['constrained_columns']):<20} {fk['referred_table']:<30} {', '.join(fk['referred_columns'])}")
        else:
            print("Nenhuma chave estrangeira encontrada.")
        
        return True
            
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        return False
    finally:
        # Garantir que a sessão seja fechada
        if session:
            session.close()
        print("\n" + "=" * 80)
        print(" VERIFICAÇÃO CONCLUÍDA ".center(80, '='))
        print("=" * 80 + "\n")

if __name__ == "__main__":
    verificar_tabela()
