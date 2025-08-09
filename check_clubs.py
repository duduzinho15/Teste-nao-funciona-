#!/usr/bin/env python3
"""
Script para verificar os clubes existentes no banco de dados.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'apostapro_db'),
    'user': os.getenv('DB_USER', 'apostapro_user'),
    'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
}

# String de conexão
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

def check_clubs():
    """Verifica os clubes existentes no banco de dados."""
    try:
        # Cria a conexão com o banco de dados
        engine = create_engine(DATABASE_URL)
        
        # Cria uma sessão
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Query para verificar se a tabela de clubes existe
        table_exists = session.execute(
            text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'clubes'
            );
            """)
        ).scalar()
        
        if not table_exists:
            print("❌ A tabela 'clubes' não existe no banco de dados.")
            return
        
        # Conta o número de clubes
        count = session.execute(text("SELECT COUNT(*) FROM clubes;")).scalar()
        print(f"✅ Tabela 'clubes' encontrada com {count} registros.")
        
        # Lista os primeiros 5 clubes
        if count > 0:
            print("\n📋 Lista de clubes (máx. 5):")
            clubs = session.execute(text("SELECT id, nome, pais, divisao FROM clubes LIMIT 5;")).fetchall()
            for club in clubs:
                print(f"- ID: {club[0]}, Nome: {club[1]}, País: {club[2]}, Divisão: {club[3]}")
        
        # Verifica se existem posts de redes sociais
        posts_count = session.execute(text("SELECT COUNT(*) FROM posts_redes_sociais;")).scalar()
        print(f"\n📊 Total de posts de redes sociais: {posts_count}")
        
        if posts_count > 0:
            print("\n📋 Últimos posts (máx. 3):")
            posts = session.execute(
                text("""
                SELECT p.id, c.nome, p.rede_social, p.data_postagem, p.curtidas 
                FROM posts_redes_sociais p
                JOIN clubes c ON p.clube_id = c.id
                ORDER BY p.data_postagem DESC
                LIMIT 3;
                """)
            ).fetchall()
            
            for post in posts:
                print(f"- ID: {post[0]}, Clube: {post[1]}, Rede: {post[2]}, Data: {post[3]}, Curtidas: {post[4]}")
        
    except Exception as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
    finally:
        if 'session' in locals():
            session.close()
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🔍 Verificando clubes no banco de dados...")
    check_clubs()
