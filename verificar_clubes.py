#!/usr/bin/env python3
"""
Script para verificar clubes existentes no banco de dados.
"""
import os
import sys
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório raiz ao path para importar os modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa os modelos e configurações
from Coleta_de_dados.database import models
from Coleta_de_dados.database.config import DatabaseSettings, db_manager

def main():
    """Função principal para verificar clubes no banco de dados."""
    print("🔍 Conectando ao banco de dados...")
    
    try:
        # Usa o db_manager para obter uma sessão
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_manager.engine)
        session = SessionLocal()
        
        # Verifica se a tabela de clubes existe
        if not db_manager.engine.dialect.has_table(db_manager.engine, 'clubes'):
            print("❌ A tabela 'clubes' não existe no banco de dados.")
            return False
        
        # Consulta os clubes usando SQL puro para evitar problemas com modelos
        print("\n🏆 Clubes cadastrados no banco de dados:")
        result = session.execute(text("SELECT id, nome FROM clubes ORDER BY id"))
        clubes = result.fetchall()
        
        if not clubes:
            print("❌ Nenhum clube encontrado no banco de dados.")
            print("\nℹ️ Para popular o banco com clubes de teste, execute o script seed_test_data.py")
        else:
            for clube in clubes:
                print(f"- ID: {clube.id}, Nome: {clube.nome}")
        
        print(f"\n✅ Total de clubes encontrados: {len(clubes)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main()
