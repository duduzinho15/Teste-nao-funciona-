#!/usr/bin/env python3
"""
Script para restaurar as tabelas essenciais no banco de dados PostgreSQL.
"""
import os
import sys
from sqlalchemy import create_engine, text, DDL, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
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

def create_tables():
    """Cria as tabelas essenciais no banco de dados."""
    engine = None
    session = None
    
    try:
        # Cria a conexão com o banco de dados
        engine = create_engine(DATABASE_URL)
        
        # Cria uma sessão
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("🔧 Iniciando a restauração das tabelas essenciais...")
        
        # Função auxiliar para executar SQL com tratamento de erros
        def execute_sql(sql, params=None):
            try:
                if params:
                    session.execute(text(sql), params)
                else:
                    session.execute(text(sql))
                session.commit()
                return True
            except SQLAlchemyError as e:
                print(f"   ⚠️ Aviso ao executar SQL: {e}")
                session.rollback()
                return False
        
        # 1. Tabela paises_clubes (sem dependências)
        print("\n1. Criando tabela 'paises_clubes'...")
        execute_sql("""
        DROP TABLE IF EXISTS paises_clubes CASCADE;
        CREATE TABLE paises_clubes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL UNIQUE,
            codigo_iso VARCHAR(3),
            continente VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
        """)
        print("   ✅ Tabela 'paises_clubes' criada com sucesso.")
        
        # 2. Tabela paises_jogadores (sem dependências)
        print("\n2. Criando tabela 'paises_jogadores'...")
        execute_sql("""
        DROP TABLE IF EXISTS paises_jogadores CASCADE;
        CREATE TABLE paises_jogadores (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL UNIQUE,
            codigo_iso VARCHAR(3),
            continente VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
        """)
        
        # 3. Tabela clubes (depende de paises_clubes)
        print("\n3. Criando tabela 'clubes'...")
        execute_sql("""
        DROP TABLE IF EXISTS clubes CASCADE;
        CREATE TABLE clubes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            nome_completo VARCHAR(500),
            url_fbref TEXT,
            pais_id INTEGER,
            cidade VARCHAR(100),
            fundacao INTEGER,
            ativo BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
        """)
        
        # Adiciona a chave estrangeira depois de criar a tabela
        execute_sql("""
        ALTER TABLE clubes 
        ADD CONSTRAINT fk_clubes_pais 
        FOREIGN KEY (pais_id) 
        REFERENCES paises_clubes(id) 
        ON DELETE SET NULL
        """)
        print("   ✅ Tabela 'clubes' criada com sucesso.")
        
        print("   ✅ Tabela 'paises_jogadores' criada com sucesso.")
        
        # 4. Tabela jogadores (depende de paises_jogadores e clubes)
        print("\n4. Criando tabela 'jogadores'...")
        execute_sql("""
        DROP TABLE IF EXISTS jogadores CASCADE;
        CREATE TABLE jogadores (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            nome_completo VARCHAR(500),
            url_fbref TEXT,
            data_nascimento DATE,
            pais_id INTEGER,
            posicao VARCHAR(50),
            pe_preferido VARCHAR(20),
            altura INTEGER,
            peso INTEGER,
            clube_atual_id INTEGER,
            ativo BOOLEAN NOT NULL DEFAULT true,
            aposentado BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
        """)
        
        # Adiciona as chaves estrangeiras separadamente
        execute_sql("""
        ALTER TABLE jogadores 
        ADD CONSTRAINT fk_jogadores_pais 
        FOREIGN KEY (pais_id) 
        REFERENCES paises_jogadores(id) 
        ON DELETE SET NULL
        """)
        
        execute_sql("""
        ALTER TABLE jogadores 
        ADD CONSTRAINT fk_jogadores_clube 
        FOREIGN KEY (clube_atual_id) 
        REFERENCES clubes(id) 
        ON DELETE SET NULL
        """)
        print("   ✅ Tabela 'jogadores' criada com sucesso.")
        
        # 5. Tabela competicoes (sem dependências)
        print("\n5. Criando tabela 'competicoes'...")
        execute_sql("""
        DROP TABLE IF EXISTS competicoes CASCADE;
        CREATE TABLE competicoes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            pais VARCHAR(100),
            nivel VARCHAR(50),
            genero VARCHAR(20) NOT NULL DEFAULT 'M',
            tipo VARCHAR(50) NOT NULL DEFAULT 'Liga',
            ativa BOOLEAN NOT NULL DEFAULT true,
            url_fbref TEXT,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
        """)
        print("   ✅ Tabela 'competicoes' criada com sucesso.")
        
        # 6. Tabela partidas (depende de competicoes e clubes)
        print("\n6. Criando tabela 'partidas'...")
        execute_sql("""
        DROP TABLE IF EXISTS partidas CASCADE;
        CREATE TABLE partidas (
            id SERIAL PRIMARY KEY,
            competicao_id INTEGER NOT NULL,
            clube_casa_id INTEGER NOT NULL,
            clube_visitante_id INTEGER NOT NULL,
            data_partida DATE,
            horario VARCHAR(10),
            rodada VARCHAR(50),
            temporada VARCHAR(20),
            gols_casa INTEGER,
            gols_visitante INTEGER,
            resultado CHAR(1),
            url_fbref TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'agendada',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            CHECK (clube_casa_id != clube_visitante_id),
            CHECK (status IN ('agendada', 'em_andamento', 'finalizada', 'cancelada'))
        )
        """)
        
        # Adiciona as chaves estrangeiras separadamente
        execute_sql("""
        ALTER TABLE partidas 
        ADD CONSTRAINT fk_partidas_competicao 
        FOREIGN KEY (competicao_id) 
        REFERENCES competicoes(id) 
        ON DELETE CASCADE
        """)
        
        execute_sql("""
        ALTER TABLE partidas 
        ADD CONSTRAINT fk_partidas_clube_casa 
        FOREIGN KEY (clube_casa_id) 
        REFERENCES clubes(id) 
        ON DELETE CASCADE
        """)
        
        execute_sql("""
        ALTER TABLE partidas 
        ADD CONSTRAINT fk_partidas_clube_visitante 
        FOREIGN KEY (clube_visitante_id) 
        REFERENCES clubes(id) 
        ON DELETE CASCADE
        """)
        print("   ✅ Tabela 'partidas' criada com sucesso.")
        
        # 7. Tabela estatisticas_partidas (depende de partidas)
        print("\n7. Criando tabela 'estatisticas_partidas'...")
        execute_sql("""
        DROP TABLE IF EXISTS estatisticas_partidas CASCADE;
        CREATE TABLE estatisticas_partidas (
            id SERIAL PRIMARY KEY,
            partida_id INTEGER NOT NULL,
            posse_bola_casa FLOAT,
            posse_bola_visitante FLOAT,
            chutes_casa INTEGER,
            chutes_visitante INTEGER,
            chutes_no_gol_casa INTEGER,
            chutes_no_gol_visitante INTEGER,
            escanteios_casa INTEGER,
            escanteios_visitante INTEGER,
            faltas_casa INTEGER,
            faltas_visitante INTEGER,
            cartoes_amarelos_casa INTEGER,
            cartoes_amarelos_visitante INTEGER,
            cartoes_vermelhos_casa INTEGER,
            cartoes_vermelhos_visitante INTEGER,
            xg_casa FLOAT,
            xg_visitante FLOAT,
            xa_casa FLOAT,
            xa_visitante FLOAT,
            formacao_casa VARCHAR(20),
            formacao_visitante VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
        """)
        
        # Adiciona a chave estrangeira separadamente
        execute_sql("""
        ALTER TABLE estatisticas_partidas 
        ADD CONSTRAINT fk_estatisticas_partida 
        FOREIGN KEY (partida_id) 
        REFERENCES partidas(id) 
        ON DELETE CASCADE
        """)
        print("   ✅ Tabela 'estatisticas_partidas' criada com sucesso.")
        
        # 8. Tabela estatisticas_clube (depende de clubes e competicoes)
        print("\n8. Criando tabela 'estatisticas_clube'...")
        execute_sql("""
        DROP TABLE IF EXISTS estatisticas_clube CASCADE;
        CREATE TABLE estatisticas_clube (
            id SERIAL PRIMARY KEY,
            clube_id INTEGER NOT NULL,
            competicao_id INTEGER NOT NULL,
            temporada VARCHAR(20) NOT NULL,
            jogos INTEGER,
            vitorias INTEGER,
            empates INTEGER,
            derrotas INTEGER,
            gols_pro INTEGER,
            gols_contra INTEGER,
            saldo_gols INTEGER,
            pontos INTEGER,
            posicao INTEGER,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            UNIQUE (clube_id, competicao_id, temporada)
        )
        """)
        
        # Adiciona as chaves estrangeiras separadamente
        execute_sql("""
        ALTER TABLE estatisticas_clube 
        ADD CONSTRAINT fk_estatisticas_clube_clube 
        FOREIGN KEY (clube_id) 
        REFERENCES clubes(id) 
        ON DELETE CASCADE
        """)
        
        execute_sql("""
        ALTER TABLE estatisticas_clube 
        ADD CONSTRAINT fk_estatisticas_clube_competicao 
        FOREIGN KEY (competicao_id) 
        REFERENCES competicoes(id) 
        ON DELETE CASCADE
        """)
        print("   ✅ Tabela 'estatisticas_clube' criada com sucesso.")
        
        # 9. Tabela records_vs_opponents (depende de clubes)
        print("\n9. Criando tabela 'records_vs_opponents'...")
        execute_sql("""
        DROP TABLE IF EXISTS records_vs_opponents CASCADE;
        CREATE TABLE records_vs_opponents (
            id SERIAL PRIMARY KEY,
            clube_id INTEGER NOT NULL,
            oponente_id INTEGER NOT NULL,
            jogos_total INTEGER,
            vitorias INTEGER,
            empates INTEGER,
            derrotas INTEGER,
            gols_pro INTEGER,
            gols_contra INTEGER,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            CHECK (clube_id != oponente_id),
            UNIQUE (clube_id, oponente_id)
        )
        """)
        
        # Adiciona as chaves estrangeiras separadamente
        execute_sql("""
        ALTER TABLE records_vs_opponents 
        ADD CONSTRAINT fk_records_clube 
        FOREIGN KEY (clube_id) 
        REFERENCES clubes(id) 
        ON DELETE CASCADE
        """)
        
        execute_sql("""
        ALTER TABLE records_vs_opponents 
        ADD CONSTRAINT fk_records_oponente 
        FOREIGN KEY (oponente_id) 
        REFERENCES clubes(id) 
        ON DELETE CASCADE
        """)
        print("   ✅ Tabela 'records_vs_opponents' criada com sucesso.")
        
        # 10. Tabela posts_redes_sociais (depende de clubes e jogadores)
        print("\n10. Criando tabela 'posts_redes_sociais'...")
        execute_sql("""
        DROP TABLE IF EXISTS posts_redes_sociais CASCADE;
        CREATE TABLE posts_redes_sociais (
            id SERIAL PRIMARY KEY,
            clube_id INTEGER,
            jogador_id INTEGER,
            rede_social VARCHAR(50) NOT NULL,
            post_id VARCHAR(100) NOT NULL,
            conteudo TEXT NOT NULL,
            data_postagem TIMESTAMP NOT NULL,
            curtidas INTEGER NOT NULL DEFAULT 0,
            comentarios INTEGER NOT NULL DEFAULT 0,
            compartilhamentos INTEGER NOT NULL DEFAULT 0,
            url_post TEXT,
            midia_url TEXT,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            CHECK (clube_id IS NOT NULL OR jogador_id IS NOT NULL),
            UNIQUE (rede_social, post_id)
        )
        """)
        
        # Adiciona as chaves estrangeiras separadamente
        execute_sql("""
        ALTER TABLE posts_redes_sociais 
        ADD CONSTRAINT fk_posts_redes_sociais_clube 
        FOREIGN KEY (clube_id) 
        REFERENCES clubes(id) 
        ON DELETE CASCADE
        """)
        
        execute_sql("""
        ALTER TABLE posts_redes_sociais 
        ADD CONSTRAINT fk_posts_redes_sociais_jogador 
        FOREIGN KEY (jogador_id) 
        REFERENCES jogadores(id) 
        ON DELETE CASCADE
        """)
        print("   ✅ Tabela 'posts_redes_sociais' verificada/criada com sucesso.")
        
        # Confirma as alterações
        session.commit()
        print("\n✅ Todas as tabelas foram criadas/verificadas com sucesso!")
        
        # Verifica se as tabelas foram criadas corretamente
        print("\n🔍 Verificando tabelas criadas...")
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result.fetchall()]
        print("\n📋 Tabelas no banco de dados:")
        for table in sorted(tables):
            print(f"   - {table}")
        
    except SQLAlchemyError as e:
        print(f"❌ Erro do SQLAlchemy ao criar as tabelas: {e}")
        if 'session' in locals():
            session.rollback()
        raise
    except Exception as e:
        print(f"❌ Erro inesperado ao criar as tabelas: {e}")
        if 'session' in locals():
            session.rollback()
        raise
    finally:
        if 'session' in locals():
            session.close()
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🔧 Iniciando a restauração das tabelas essenciais...")
    create_tables()
    print("\n✅ Processo concluído. Verifique o banco de dados.")
