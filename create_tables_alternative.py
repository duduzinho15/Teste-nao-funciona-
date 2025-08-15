# create_tables_alternative.py
from Coleta_de_dados.database.config import DatabaseManager
from Coleta_de_dados.database.models import Base

print("Tentando criar tabelas usando SQLAlchemy create_all()...")
try:
    db_manager = DatabaseManager()
    engine = db_manager.engine
    
    print("Criando todas as tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    
    # Verificar se as tabelas foram criadas
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result.fetchall()]
        print(f"Tabelas existentes após criação ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")
    
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
    print("Tentando abordagem alternativa...")
    
    # Tentar criar apenas as tabelas essenciais uma por vez
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Criar tabela alembic_version
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                );
            """))
            print("✅ Tabela alembic_version criada")
            
            # Criar tabela posts_redes_sociais
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS posts_redes_sociais (
                    id SERIAL PRIMARY KEY,
                    clube_id INTEGER REFERENCES clubes(id),
                    jogador_id INTEGER,
                    plataforma VARCHAR(100),
                    conteudo TEXT,
                    data_post TIMESTAMP,
                    likes INTEGER DEFAULT 0,
                    comentarios INTEGER DEFAULT 0,
                    compartilhamentos INTEGER DEFAULT 0,
                    sentimento_positivo DECIMAL(5,4),
                    sentimento_negativo DECIMAL(5,4),
                    sentimento_neutro DECIMAL(5,4),
                    sentimento_composto DECIMAL(5,4),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            print("✅ Tabela posts_redes_sociais criada")
            
            # Criar tabela noticias_clubes
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS noticias_clubes (
                    id SERIAL PRIMARY KEY,
                    clube_id INTEGER REFERENCES clubes(id),
                    titulo VARCHAR(500),
                    conteudo TEXT,
                    fonte VARCHAR(200),
                    url VARCHAR(500),
                    data_publicacao TIMESTAMP,
                    sentimento_positivo DECIMAL(5,4),
                    sentimento_negativo DECIMAL(5,4),
                    sentimento_neutro DECIMAL(5,4),
                    sentimento_composto DECIMAL(5,4),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            print("✅ Tabela noticias_clubes criada")
            
            # Criar tabela recomendacoes_apostas
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS recomendacoes_apostas (
                    id SERIAL PRIMARY KEY,
                    partida_id INTEGER REFERENCES partidas(id),
                    mercado_aposta VARCHAR(100),
                    previsao VARCHAR(100),
                    probabilidade DECIMAL(5,4),
                    odd_justa DECIMAL(8,2),
                    rating DECIMAL(3,2),
                    confianca_modelo DECIMAL(5,4),
                    modelo_utilizado VARCHAR(100),
                    features_utilizadas TEXT,
                    status VARCHAR(50) DEFAULT 'pendente',
                    resultado_real VARCHAR(100),
                    roi DECIMAL(8,4),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            print("✅ Tabela recomendacoes_apostas criada")
            
            conn.commit()
            print("✅ Todas as tabelas essenciais foram criadas!")
            
    except Exception as e2:
        print(f"❌ Erro na abordagem alternativa: {e2}")
        raise
