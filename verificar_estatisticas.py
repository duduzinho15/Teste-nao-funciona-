#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar o conteúdo da tabela estatisticas_partidas.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

def main():
    # Configuração da conexão com o banco de dados
    db_url = "postgresql://apostapro_user:apostapro_pass@localhost:5432/apostapro_db"
    engine = create_engine(db_url)
    
    # Criar uma sessão
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Verificar se a tabela existe
        inspector = inspect(engine)
        table_exists = 'estatisticas_partidas' in inspector.get_table_names()
        print(f"Tabela 'estatisticas_partidas' existe: {table_exists}")
        
        if table_exists:
            # Obter informações sobre as colunas da tabela
            columns = inspector.get_columns('estatisticas_partidas')
            print("\nColunas da tabela 'estatisticas_partidas':")
            for column in columns:
                print(f"- {column['name']}: {column['type']}")
            
            # Contar o número de registros
            count = session.execute(text("SELECT COUNT(*) FROM estatisticas_partidas")).scalar()
            print(f"\nTotal de registros em 'estatisticas_partidas': {count}")
            
            # Mostrar alguns registros de exemplo
            if count > 0:
                print("\nExemplo de registros (limite 5):")
                result = session.execute(text("SELECT * FROM estatisticas_partidas LIMIT 5")).fetchall()
                for row in result:
                    print(row)
        else:
            print("A tabela 'estatisticas_partidas' não existe no banco de dados.")
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
    
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    main()
