#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from sqlalchemy import create_engine, inspect

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def list_all_tables():
    """Lista todas as tabelas no banco de dados."""
    try:
        # Importar configurações do banco de dados
        from Coleta_de_dados.database.config import db_manager
        
        print("✅ Módulo de configuração do banco de dados importado com sucesso!")
        
        # Criar engine e inspetor
        engine = db_manager.engine
        inspector = inspect(engine)
        
        # Listar todas as tabelas
        tables = inspector.get_table_names()
        print("\n📋 Tabelas no banco de dados:")
        for table in sorted(tables):
            print(f"- {table}")
        
        # Verificar se há tabelas relacionadas a redes sociais
        social_tables = [t for t in tables if 'rede' in t.lower() or 'social' in t.lower() or 'post' in t.lower()]
        
        if social_tables:
            print("\n🔍 Tabelas relacionadas a redes sociais:")
            for table in social_tables:
                print(f"- {table}")
        else:
            print("\nℹ️ Nenhuma tabela relacionada a redes sociais encontrada.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao listar as tabelas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Listando todas as tabelas no banco de dados...")
    if list_all_tables():
        print("\n✅ Listagem concluída com sucesso!")
    else:
        print("\n❌ Ocorreram erros durante a listagem.")
        sys.exit(1)
