#!/usr/bin/env python3
"""
Script para popular o banco de dados com clubes de teste.
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório raiz ao path para importar os modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa as configurações do banco de dados
from Coleta_de_dados.database.config import db_manager

def verificar_tabela_existe(session, tabela):
    """Verifica se uma tabela existe no banco de dados."""
    try:
        # Consulta o catálogo do PostgreSQL para verificar se a tabela existe
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = :tabela
        );
        """
        result = session.execute(text(query), {"tabela": tabela})
        return result.scalar()
    except Exception as e:
        print(f"⚠️ Erro ao verificar a tabela {tabela}: {e}")
        return False

def criar_tabelas_se_nao_existirem(session):
    """Cria as tabelas necessárias se elas não existirem."""
    try:
        # Verifica e cria a tabela de países de clubes se não existir
        if not verificar_tabela_existe(session, 'paises_clubes'):
            session.execute(text("""
                CREATE TABLE paises_clubes (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL UNIQUE,
                    codigo_iso VARCHAR(3),
                    continente VARCHAR(50)
                )
            """))
            session.commit()
            print("✅ Tabela 'paises_clubes' criada com sucesso.")
        
        # Verifica e cria a tabela de clubes se não existir
        if not verificar_tabela_existe(session, 'clubes'):
            session.execute(text("""
                CREATE TABLE clubes (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    nome_completo VARCHAR(500),
                    url_fbref TEXT,
                    pais_id INTEGER REFERENCES paises_clubes(id),
                    cidade VARCHAR(100),
                    fundacao INTEGER,
                    ativo BOOLEAN DEFAULT TRUE NOT NULL
                )
            """))
            session.commit()
            print("✅ Tabela 'clubes' criada com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao verificar/criar tabelas: {e}")
        session.rollback()
        raise

def inserir_paises_teste(session):
    """Insere países de teste na tabela paises_clubes."""
    paises = [
        ("Brasil", "BRA", "América do Sul"),
        ("Argentina", "ARG", "América do Sul"),
        ("Espanha", "ESP", "Europa"),
        ("Inglaterra", "ENG", "Europa"),
        ("Itália", "ITA", "Europa"),
    ]
    
    try:
        # Verifica se já existem países cadastrados
        result = session.execute(text("SELECT COUNT(*) FROM paises_clubes"))
        count = result.scalar()
        
        if count == 0:
            print("\n🌎 Inserindo países de teste...")
            for pais in paises:
                session.execute(
                    text("""
                        INSERT INTO paises_clubes (nome, codigo_iso, continente)
                        VALUES (:nome, :codigo_iso, :continente)
                        ON CONFLICT (nome) DO NOTHING
                    """),
                    {"nome": pais[0], "codigo_iso": pais[1], "continente": pais[2]}
                )
            session.commit()
            print(f"✅ {len(paises)} países inseridos com sucesso.")
        else:
            print(f"ℹ️ Encontrados {count} países já cadastrados no banco de dados.")
            
        # Retorna o mapeamento de nomes para IDs dos países
        result = session.execute(text("SELECT id, nome FROM paises_clubes"))
        return {nome: id for id, nome in result.fetchall()}
        
    except Exception as e:
        print(f"❌ Erro ao inserir países: {e}")
        session.rollback()
        raise

def inserir_clubes_teste(session, paises_dict):
    """Insere clubes de teste na tabela clubes.
    
    Args:
        session: Sessão do banco de dados
        paises_dict: Dicionário mapeando nomes de países para seus IDs
    """
    try:
        # Verifica se já existem clubes cadastrados
        result = session.execute(text("SELECT COUNT(*) FROM clubes"))
        count = result.scalar()
        
        if count == 0:
            print("\n⚽ Inserindo clubes de teste...")
            
            # Lista de clubes com seus respectivos países
            clubes = [
                ("Flamengo", "Clube de Regatas do Flamengo", "https://fbref.com/en/squads/598bc722/2023-2024/Flamengo-Stats", "Rio de Janeiro", 1895, "Brasil"),
                ("Palmeiras", "Sociedade Esportiva Palmeiras", "https://fbref.com/en/squads/1c59e5fa/2023-2024/Palmeiras-Stats", "São Paulo", 1914, "Brasil"),
                ("River Plate", "Club Atlético River Plate", "https://fbref.com/en/squads/7e9e1e6a/2023-2024/River-Plate-Stats", "Buenos Aires", 1901, "Argentina"),
                ("Barcelona", "Futbol Club Barcelona", "https://fbref.com/en/squads/206d90db/2023-2024/Barcelona-Stats", "Barcelona", 1899, "Espanha"),
                ("Real Madrid", "Real Madrid Club de Fútbol", "https://fbref.com/en/squads/53a2f082/2023-2024/Real-Madrid-Stats", "Madrid", 1902, "Espanha"),
                ("Manchester City", "Manchester City Football Club", "https://fbref.com/en/squads/b8fd03ef/2023-2024/Manchester-City-Stats", "Manchester", 1880, "Inglaterra"),
                ("Liverpool", "Liverpool Football Club", "https://fbref.com/en/squads/822bd0ba/2023-2024/Liverpool-Stats", "Liverpool", 1892, "Inglaterra"),
                ("Juventus", "Juventus Football Club", "https://fbref.com/en/squads/e0652b02/2023-2024/Juventus-Stats", "Turim", 1897, "Itália"),
                ("Internazionale", "Football Club Internazionale Milano", "https://fbref.com/en/squads/d609edc0/2023-2024/Internazionale-Stats", "Milão", 1908, "Itália"),
            ]
            
            # Insere cada clube
            for clube in clubes:
                nome, nome_completo, url_fbref, cidade, fundacao, pais_nome = clube
                
                # Obtém o ID do país
                pais_id = paises_dict.get(pais_nome)
                if not pais_id:
                    print(f"⚠️ País não encontrado para o clube {nome}: {pais_nome}")
                    continue
                
                # Insere o clube
                session.execute(
                    text("""
                        INSERT INTO clubes (nome, nome_completo, url_fbref, cidade, fundacao, pais_id)
                        VALUES (:nome, :nome_completo, :url_fbref, :cidade, :fundacao, :pais_id)
                        ON CONFLICT (nome) DO NOTHING
                    """),
                    {
                        "nome": nome, 
                        "nome_completo": nome_completo,
                        "url_fbref": url_fbref,
                        "cidade": cidade,
                        "fundacao": fundacao,
                        "pais_id": pais_id
                    }
                )
                
            session.commit()
            print(f"✅ {len(clubes)} clubes inseridos com sucesso.")
            
            # Retorna o mapeamento de nomes para IDs dos clubes
            result = session.execute(text("SELECT id, nome FROM clubes"))
            return {nome: id for id, nome in result.fetchall()}
            
        else:
            print(f"ℹ️ Encontrados {count} clubes já cadastrados no banco de dados.")
            
            # Retorna o mapeamento de nomes para IDs dos clubes existentes
            result = session.execute(text("SELECT id, nome FROM clubes"))
            return {nome: id for id, nome in result.fetchall()}
            
    except Exception as e:
        print(f"❌ Erro ao inserir clubes: {e}")
        session.rollback()
        raise

def main():
    """Função principal para popular o banco de dados com clubes de teste."""
    print("🚀 Iniciando a população do banco de dados com clubes de teste...")
    
    try:
        # Cria uma sessão
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_manager.engine)
        session = SessionLocal()
        
        # Cria as tabelas se não existirem
        print("\n🔄 Verificando/Criando tabelas necessárias...")
        criar_tabelas_se_nao_existirem(session)
        
        # Insere países de teste e obtém o mapeamento de nomes para IDs
        paises_dict = inserir_paises_teste(session)
        
        if not paises_dict:
            print("❌ Falha ao obter os países. Verifique o banco de dados.")
            return False
            
        # Insere clubes de teste
        clubes_dict = inserir_clubes_teste(session, paises_dict)
        
        if not clubes_dict:
            print("❌ Falha ao obter os clubes. Verifique o banco de dados.")
            return False
        
        # Lista os clubes inseridos
        print("\n🏆 Clubes cadastrados no banco de dados:")
        result = session.execute(text("""
            SELECT c.id, c.nome, p.nome as pais 
            FROM clubes c 
            JOIN paises_clubes p ON c.pais_id = p.id 
            ORDER BY c.id
        """))
        
        clubes = result.fetchall()
        if not clubes:
            print("ℹ️ Nenhum clube encontrado no banco de dados.")
        else:
            for clube in clubes:
                print(f"- ID: {clube.id}, Nome: {clube.nome}, País: {clube.pais}")
        
        print(f"\n✨ Processo concluído com sucesso! Total de clubes: {len(clubes)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao popular o banco de dados: {e}")
        import traceback
        traceback.print_exc()
        if 'session' in locals():
            session.rollback()
        return False
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main()
