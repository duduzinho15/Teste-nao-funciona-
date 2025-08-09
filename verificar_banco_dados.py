#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar o conteúdo do banco de dados.
"""

import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

def main():
    # Configuração da conexão com o banco de dados
    db_url = "postgresql://apostapro_user:apostapro_pass@localhost:5432/apostapro_db"
    engine = create_engine(db_url)
    
    # Criar uma sessão
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Obter o inspetor
        inspector = inspect(engine)
        
        # Listar todas as tabelas
        print("\n=== TABELAS NO BANCO DE DADOS ===")
        tabelas = inspector.get_table_names()
        for tabela in tabelas:
            print(f"\nTabela: {tabela}")
            
            # Obter colunas da tabela
            colunas = inspector.get_columns(tabela)
            print(f"  Colunas ({len(colunas)}):")
            for coluna in colunas:
                print(f"  - {coluna['name']}: {coluna['type']}")
            
            # Contar registros
            try:
                count = session.execute(f"SELECT COUNT(*) FROM {tabela}").scalar()
                print(f"  Total de registros: {count}")
                
                # Mostrar alguns registros de exemplo
                if count > 0:
                    print("  Exemplo de registros (limite 2):")
                    result = session.execute(f"SELECT * FROM {tabela} LIMIT 2").fetchall()
                    for row in result:
                        print(f"  {row}")
            except Exception as e:
                print(f"  Erro ao contar registros: {e}")
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
    
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    main()
