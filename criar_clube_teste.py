"""
Script para criar um clube de teste no banco de dados.

Este script adiciona um clube de teste ao banco de dados para permitir
a execução de testes na API de redes sociais.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Adiciona o diretório raiz ao path do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def criar_clube_teste():
    """Cria um clube de teste no banco de dados."""
    try:
        # Conecta ao banco de dados SQLite
        db_path = os.path.join(os.path.dirname(__file__), 'fbref_data.db')
        engine = create_engine(f'sqlite:///{db_path}')
        
        # Cria uma sessão
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verifica se já existe um país de teste
        result = session.execute(
            text("SELECT id FROM paises_clubes WHERE nome = 'Brasil'")
        ).fetchone()
        
        pais_id = None
        if result:
            pais_id = result[0]
        else:
            # Cria um país de teste se não existir
            result = session.execute(
                text("""
                INSERT INTO paises_clubes (nome, codigo_iso, continente)
                VALUES ('Brasil', 'BRA', 'América do Sul')
                RETURNING id
                """)
            ).fetchone()
            pais_id = result[0]
            session.commit()
            print(f"✅ País de teste criado com sucesso! ID: {pais_id}")
        
        # Verifica se já existe um clube de teste
        result = session.execute(
            text("SELECT id FROM clubes WHERE nome = 'Clube de Teste API'")
        ).fetchone()
        
        if result:
            print(f"ℹ️  Clube de teste já existe no banco de dados. ID: {result[0]}")
            session.close()
            return result[0]
        
        # Cria um clube de teste
        result = session.execute(
            text("""
            INSERT INTO clubes (
                nome, nome_completo, url_fbref, pais_id, cidade, 
                fundacao, ativo, created_at, updated_at
            ) VALUES (
                'Clube de Teste API', 
                'Clube de Teste para API de Redes Sociais', 
                'https://example.com/teste', 
                :pais_id, 
                'Cidade de Teste', 
                1900, 
                1, 
                :agora, 
                :agora
            )
            RETURNING id
            """),
            {"pais_id": pais_id, "agora": datetime.now()}
        ).fetchone()
        
        clube_id = result[0]
        session.commit()
        print(f"✅ Clube de teste criado com sucesso! ID: {clube_id}")
        
        # Cria alguns posts de teste para o clube
        posts = [
            {
                "clube_id": clube_id,
                "conteudo": "Primeiro post de teste da API",
                "url": "https://example.com/post/1",
                "data_postagem": "2025-08-01 10:00:00",
                "rede_social": "twitter",
                "engajamento": 100,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "clube_id": clube_id,
                "conteudo": "Segundo post de teste com mais engajamento",
                "url": "https://example.com/post/2",
                "data_postagem": "2025-08-02 15:30:00",
                "rede_social": "instagram",
                "engajamento": 250,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        # Verifica se a tabela de posts existe
        result = session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='posts_redes_sociais'")
        ).fetchone()
        
        if result:
            # Insere os posts de teste
            for post in posts:
                session.execute(
                    text("""
                    INSERT INTO posts_redes_sociais (
                        clube_id, conteudo, url, data_postagem, 
                        rede_social, engajamento, created_at, updated_at
                    ) VALUES (
                        :clube_id, :conteudo, :url, :data_postagem, 
                        :rede_social, :engajamento, :created_at, :updated_at
                    )
                    """),
                    post
                )
            
            session.commit()
            print(f"✅ {len(posts)} posts de teste criados com sucesso!")
        else:
            print("ℹ️  Tabela 'posts_redes_sociais' não encontrada. Apenas o clube foi criado.")
        
        session.close()
        return clube_id
        
    except Exception as e:
        print(f"❌ Erro ao criar clube de teste: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return None

if __name__ == "__main__":
    clube_id = criar_clube_teste()
    if clube_id:
        print(f"\n✅ Configuração de teste concluída com sucesso!")
        print(f"   ID do Clube de Teste: {clube_id}")
        print("\nVocê pode usar este ID para testar os endpoints da API.")
    else:
        print("\n❌ Falha ao configurar o ambiente de teste.")
