#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar a conexão com o banco de dados e a existência das tabelas.
"""
import sys
import os
import logging
from sqlalchemy import inspect, text, create_engine
from sqlalchemy.orm import sessionmaker

# Configura o encoding para UTF-8
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configura o logging para exibir mensagens de depuração
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Adiciona o diretório raiz ao path para importar as configurações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa as configurações do banco de dados
try:
    from Coleta_de_dados.database.config import db_manager
    print("✅ Módulo de configuração do banco de dados importado com sucesso.")
except ImportError as e:
    print(f"❌ Erro ao importar configurações do banco de dados: {e}")
    print("Verifique se o módulo 'Coleta_de_dados.database.config' existe e está acessível.")
    sys.exit(1)

def verificar_conexao():
    """Verifica se é possível conectar ao banco de dados."""
    try:
        # Tenta conectar ao banco de dados
        with db_manager.engine.connect() as conn:
            # Executa uma consulta simples para verificar a conexão
            result = conn.execute(text("SELECT version()"))
            db_version = result.scalar()
            print(f"✅ Conexão bem-sucedida. Versão do PostgreSQL: {db_version}")
            return True
    except Exception as e:
        print(f"❌ Falha ao conectar ao banco de dados: {e}")
        return False

def verificar_tabelas():
    """Verifica se as tabelas necessárias existem no banco de dados."""
    inspector = inspect(db_manager.engine)
    tabelas_necessarias = ['paises_clubes', 'clubes']
    tabelas_existentes = inspector.get_table_names()
    
    print("\n🔍 Verificando tabelas no banco de dados:")
    
    todas_tabelas_existem = True
    for tabela in tabelas_necessarias:
        if tabela in tabelas_existentes:
            print(f"✅ Tabela '{tabela}' existe.")
        else:
            print(f"❌ Tabela '{tabela}' NÃO encontrada.")
            todas_tabelas_existem = False
    
    if not todas_tabelas_existem:
        print("\nℹ️ Algumas tabelas necessárias não foram encontradas no banco de dados.")
    else:
        print("\n✅ Todas as tabelas necessárias existem no banco de dados.")
    
    return todas_tabelas_existem

def verificar_dados_tabelas():
    """Verifica se há dados nas tabelas."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_manager.engine)
    session = SessionLocal()
    
    try:
        print("\n📊 Verificando dados nas tabelas:")
        
        # Verifica paises_clubes
        result = session.execute(text("SELECT COUNT(*) FROM paises_clubes"))
        count_paises = result.scalar()
        print(f"- paises_clubes: {count_paises} registros")
        
        # Verifica clubes
        result = session.execute(text("SELECT COUNT(*) FROM clubes"))
        count_clubes = result.scalar()
        print(f"- clubes: {count_clubes} registros")
        
        # Se houver clubes, lista alguns exemplos
        if count_clubes > 0:
            print("\n📋 Exemplos de clubes cadastrados:")
            result = session.execute(text("""
                SELECT c.id, c.nome, p.nome as pais 
                FROM clubes c 
                JOIN paises_clubes p ON c.pais_id = p.id 
                ORDER BY c.id LIMIT 5
            """))
            for clube in result.fetchall():
                print(f"- ID: {clube.id}, Nome: {clube.nome}, País: {clube.pais}")
        
        return count_paises > 0 and count_clubes > 0
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados das tabelas: {e}")
        return False
    finally:
        session.close()

def main():
    """Função principal do script de diagnóstico."""
    print("🔍 Iniciando diagnóstico do banco de dados...")
    
    # Verifica a conexão
    if not verificar_conexao():
        print("\n❌ Não foi possível continuar com o diagnóstico devido a falha na conexão.")
        return False
    
    # Verifica as tabelas
    tabelas_ok = verificar_tabelas()
    
    # Se as tabelas existirem, verifica os dados
    if tabelas_ok:
        dados_ok = verificar_dados_tabelas()
        if dados_ok:
            print("\n✅ Diagnóstico concluído com sucesso. O banco de dados parece estar configurado corretamente.")
        else:
            print("\n⚠️ O banco de dados está configurado, mas algumas tabelas podem estar vazias.")
    else:
        print("\n❌ Algumas tabelas necessárias não foram encontradas no banco de dados.")
    
    return tabelas_ok

if __name__ == "__main__":
    main()
