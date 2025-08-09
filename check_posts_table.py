#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_table_structure():
    """Verifica a estrutura da tabela posts_redes_sociais."""
    try:
        # Importar configurações do banco de dados
        from Coleta_de_dados.database.config import db_manager
        
        print("✅ Módulo de configuração do banco de dados importado com sucesso!")
        
        # Criar engine e inspetor
        engine = db_manager.engine
        inspector = inspect(engine)
        
        # Verificar se a tabela existe
        if 'posts_redes_sociais' not in inspector.get_table_names():
            print("❌ A tabela 'posts_redes_sociais' não existe no banco de dados.")
            return False
        
        # Obter informações das colunas
        print("\n📋 Estrutura da tabela 'posts_redes_sociais':")
        print("\n📝 Colunas:")
        for column in inspector.get_columns('posts_redes_sociais'):
            print(f"- {column['name']} ({column['type']})" + 
                  (" NOT NULL" if not column['nullable'] else "") +
                  (f" DEFAULT {column['default']}" if column['default'] is not None else ""))
        
        # Verificar chaves estrangeiras
        print("\n🔑 Chaves estrangeiras:")
        for fk in inspector.get_foreign_keys('posts_redes_sociais'):
            print(f"- {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
        
        # Verificar índices
        print("\n📊 Índices:")
        for index in inspector.get_indexes('posts_redes_sociais'):
            print(f"- {index['name']}: {index['column_names']} (unique: {index.get('unique', False)})")
        
        # Verificar constraints CHECK
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT conname, pg_get_constraintdef(oid) 
                FROM pg_constraint 
                WHERE conrelid = 'posts_redes_sociais'::regclass 
                AND contype = 'c';
            """))
            
            checks = result.fetchall()
            if checks:
                print("\n🔍 Constraints CHECK:")
                for name, definition in checks:
                    print(f"- {name}: {definition}")
            else:
                print("\nℹ️ Nenhuma constraint CHECK encontrada.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao verificar a estrutura da tabela: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Verificando estrutura da tabela posts_redes_sociais...")
    if check_table_structure():
        print("\n✅ Verificação concluída com sucesso!")
    else:
        print("\n❌ Ocorreram erros durante a verificação.")
        sys.exit(1)
