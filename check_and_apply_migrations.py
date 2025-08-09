#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_structure():
    """Verifica a estrutura do banco de dados."""
    try:
        # Importar configurações do banco de dados
        from Coleta_de_dados.database.config import db_manager
        
        print("✅ Módulo de configuração do banco de dados importado com sucesso!")
        
        # Criar uma conexão com o banco de dados
        engine = db_manager.engine
        inspector = inspect(engine)
        
        # Listar todas as tabelas
        print("\n📋 Tabelas no banco de dados:")
        tables = inspector.get_table_names()
        for table in tables:
            print(f"- {table}")
        
        # Verificar a tabela posts_redes_sociais
        if 'posts_redes_sociais' in tables:
            print("\n🔍 Estrutura da tabela 'posts_redes_sociais':")
            
            # Listar colunas
            print("\n📝 Colunas:")
            for column in inspector.get_columns('posts_redes_sociais'):
                print(f"- {column['name']} ({column['type']})")
            
            # Listar chaves estrangeiras
            print("\n🔑 Chaves estrangeiras:")
            for fk in inspector.get_foreign_keys('posts_redes_sociais'):
                print(f"- {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
            
            # Listar índices
            print("\n📊 Índices:")
            for index in inspector.get_indexes('posts_redes_sociais'):
                print(f"- {index['name']}: {index['column_names']} (unique: {index.get('unique', False)})")
        else:
            print("\n❌ A tabela 'posts_redes_sociais' não foi encontrada no banco de dados.")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Erro ao verificar a estrutura do banco de dados: {e}")
        import traceback
        traceback.print_exc()
        return False

def apply_migrations():
    """Aplica as migrações pendentes usando Alembic."""
    try:
        # Configurar o Alembic
        config = Config("alembic.ini")
        
        print("\n🔄 Aplicando migrações pendentes...")
        command.upgrade(config, "head")
        print("✅ Migrações aplicadas com sucesso!")
        
        # Mostrar a revisão atual
        print("\n🔍 Revisão atual do banco de dados:")
        command.current(config)
        
        return True
    except Exception as e:
        print(f"\n❌ Erro ao aplicar migrações: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Iniciando verificação da estrutura do banco de dados...")
    if check_database_structure():
        print("\n✅ Verificação concluída com sucesso!")
        
        # Perguntar se deseja aplicar migrações
        if input("\nDeseja aplicar as migrações pendentes? (s/n): ").lower() == 's':
            if apply_migrations():
                print("\n✅ Migrações aplicadas com sucesso!")
            else:
                print("\n❌ Falha ao aplicar migrações.")
    else:
        print("\n❌ Ocorreram erros durante a verificação.")
        sys.exit(1)
