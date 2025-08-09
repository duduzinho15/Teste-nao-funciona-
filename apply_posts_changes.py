#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def apply_changes():
    """Aplica as alterações necessárias na tabela posts_redes_sociais."""
    try:
        # Importar configurações do banco de dados
        from Coleta_de_dados.database.config import db_manager
        
        print("✅ Módulo de configuração do banco de dados importado com sucesso!")
        
        # Obter uma sessão do banco de dados
        session = db_manager.SessionLocal()
        
        try:
            print("\n🔧 Aplicando alterações na tabela posts_redes_sociais...")
            
            # 1. Tornar clube_id opcional
            print("\n1. Tornando clube_id opcional...")
            session.execute(text("""
                ALTER TABLE posts_redes_sociais 
                ALTER COLUMN clube_id DROP NOT NULL;
                
                COMMENT ON COLUMN posts_redes_sociais.clube_id IS 
                'ID do clube dono do post (opcional se jogador_id estiver preenchido)';
            
                -- Adicionar coluna jogador_id
                ALTER TABLE posts_redes_sociais
                ADD COLUMN IF NOT EXISTS jogador_id INTEGER 
                REFERENCES jogadores(id) ON DELETE CASCADE;
                
                COMMENT ON COLUMN posts_redes_sociais.jogador_id IS 
                'ID do jogador dono do post (opcional se clube_id estiver preenchido)';
            
                -- Adicionar índice para jogador_id
                CREATE INDEX IF NOT EXISTS idx_posts_redes_sociais_jogador 
                ON posts_redes_sociais(jogador_id);
            
                -- Adicionar constraint para garantir que pelo menos um dos IDs esteja preenchido
                ALTER TABLE posts_redes_sociais 
                ADD CONSTRAINT ck_posts_redes_sociais_owner 
                CHECK (clube_id IS NOT NULL OR jogador_id IS NOT NULL);
            
                -- Atualizar comentário da tabela
                COMMENT ON TABLE posts_redes_sociais IS 
                'Armazena posts de redes sociais de clubes e jogadores';
            
                -- Atualizar comentário das colunas
                COMMENT ON COLUMN posts_redes_sociais.rede_social IS 
                'Plataforma de rede social (ex: ''Twitter'', ''Instagram'', ''Facebook'')';
                
                COMMENT ON COLUMN posts_redes_sociais.post_id IS 
                'ID único do post na plataforma de origem';
                
                COMMENT ON COLUMN posts_redes_sociais.conteudo IS 
                'Conteúdo textual do post';
                
                COMMENT ON COLUMN posts_redes_sociais.data_postagem IS 
                'Data e hora em que o post foi publicado';
                
                COMMENT ON COLUMN posts_redes_sociais.curtidas IS 
                'Número de curtidas/reactions do post';
                
                COMMENT ON COLUMN posts_redes_sociais.comentarios IS 
                'Número de comentários no post';
                
                COMMENT ON COLUMN posts_redes_sociais.compartilhamentos IS 
                'Número de compartilhamentos/retweets';
                
                COMMENT ON COLUMN posts_redes_sociais.url_post IS 
                'URL direta para o post na rede social';
                
                COMMENT ON COLUMN posts_redes_sociais.midia_url IS 
                'URL da mídia anexada ao post (imagem/vídeo)';
            
                -- Confirmar as alterações
                COMMIT;
            
                -- Verificar se as alterações foram aplicadas
                SELECT '✅ Alterações aplicadas com sucesso!' AS resultado;
            
            
            """))
            
            print("\n✅ Alterações aplicadas com sucesso!")
            
            # Confirmar as alterações
            session.commit()
            
            # Verificar se as alterações foram aplicadas
            result = session.execute(text("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'posts_redes_sociais' 
                AND column_name = 'clube_id';
            """)).fetchone()
            
            if result and result[1] == 'YES':
                print("\n✅ clube_id agora é opcional (pode ser NULL)")
            
            # Verificar se a coluna jogador_id foi criada
            result = session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'posts_redes_sociais' 
                AND column_name = 'jogador_id';
            """)).fetchone()
            
            if result:
                print("✅ Coluna jogador_id criada com sucesso")
            
            # Verificar se o índice foi criado
            result = session.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'posts_redes_sociais' 
                AND indexname = 'idx_posts_redes_sociais_jogador';
            """)).fetchone()
            
            if result:
                print("✅ Índice idx_posts_redes_sociais_jogador criado com sucesso")
            
            # Verificar se a constraint foi criada
            result = session.execute(text("""
                SELECT conname 
                FROM pg_constraint 
                WHERE conname = 'ck_posts_redes_sociais_owner';
            """)).fetchone()
            
            if result:
                print("✅ Constraint ck_posts_redes_sociais_owner criada com sucesso")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro ao executar as alterações: {e}")
            session.rollback()
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            session.close()
    
    except Exception as e:
        print(f"\n❌ Erro ao conectar ao banco de dados: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Iniciando aplicação de alterações na tabela posts_redes_sociais...")
    if apply_changes():
        print("\n✅ Todas as alterações foram aplicadas com sucesso!")
        print("\nA tabela posts_redes_sociais agora suporta posts de jogadores e clubes.")
    else:
        print("\n❌ Ocorreram erros durante a aplicação das alterações.")
        sys.exit(1)
