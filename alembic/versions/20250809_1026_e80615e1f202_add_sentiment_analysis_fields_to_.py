"""Add sentiment analysis fields to noticias_clubes table

Revision ID: e80615e1f202
Revises: 3c958e4a60b7
Create Date: 2025-08-09 10:26:53.056199

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e80615e1f202'
down_revision = '3c958e4a60b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adiciona colunas de análise de sentimento
    op.add_column('noticias_clubes', sa.Column('sentimento_geral', sa.Float(), nullable=True, 
                  comment='Pontuação de sentimento entre -1 (negativo) e 1 (positivo)'))
    op.add_column('noticias_clubes', sa.Column('confianca_sentimento', sa.Float(), nullable=True,
                  comment='Nível de confiança da análise de sentimento (0 a 1)'))
    op.add_column('noticias_clubes', sa.Column('polaridade', sa.String(length=20), nullable=True,
                  comment='Classificação geral do sentimento (positivo, negativo, neutro)'))
    
    # Adiciona colunas para tópicos e palavras-chave
    op.add_column('noticias_clubes', sa.Column('topicos', sa.String(length=255), nullable=True,
                  comment='Tópicos principais identificados na notícia (separados por vírgula)'))
    op.add_column('noticias_clubes', sa.Column('palavras_chave', sa.String(length=500), nullable=True,
                  comment='Palavras-chave extraídas do conteúdo (separadas por vírgula)'))
    
    # Adiciona metadados da análise
    op.add_column('noticias_clubes', sa.Column('analisado_em', sa.DateTime(), nullable=True,
                  comment='Data e hora em que a análise de sentimento foi realizada'))
    op.add_column('noticias_clubes', sa.Column('modelo_analise', sa.String(length=100), nullable=True,
                  comment='Nome/versão do modelo de análise de sentimento utilizado'))
    
    # Cria índices para melhorar consultas por sentimento e polaridade
    op.create_index('idx_noticias_sentimento', 'noticias_clubes', ['sentimento_geral'])
    op.create_index('idx_noticias_polaridade', 'noticias_clubes', ['polaridade'])


def downgrade() -> None:
    # Remove índices
    op.drop_index('idx_noticias_polaridade', table_name='noticias_clubes')
    op.drop_index('idx_noticias_sentimento', table_name='noticias_clubes')
    
    # Remove colunas de metadados
    op.drop_column('noticias_clubes', 'modelo_analise')
    op.drop_column('noticias_clubes', 'analisado_em')
    
    # Remove colunas de tópicos e palavras-chave
    op.drop_column('noticias_clubes', 'palavras_chave')
    op.drop_column('noticias_clubes', 'topicos')
    
    # Remove colunas de análise de sentimento
    op.drop_column('noticias_clubes', 'polaridade')
    op.drop_column('noticias_clubes', 'confianca_sentimento')
    op.drop_column('noticias_clubes', 'sentimento_geral')
