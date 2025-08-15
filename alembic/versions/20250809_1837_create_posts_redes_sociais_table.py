"""create posts_redes_sociais table

Revision ID: 20250809_1837
Revises: 3c958e4a60b7
Create Date: 2025-08-09 18:37:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250809_1837'
down_revision = '3c958e4a60b7'
branch_labels = None
depends_on = None

def upgrade():
    # Create the posts_redes_sociais table with all necessary columns
    op.create_table(
        'posts_redes_sociais',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('clube_id', sa.Integer(), sa.ForeignKey('clubes.id', ondelete='CASCADE'), nullable=True, comment='ID do clube dono do post'),
        sa.Column('jogador_id', sa.Integer(), sa.ForeignKey('jogadores.id', ondelete='CASCADE'), nullable=True, comment='ID do jogador dono do post'),
        sa.Column('rede_social', sa.String(50), nullable=False, comment="Plataforma de rede social (ex: 'Twitter', 'Instagram', 'Facebook')"),
        sa.Column('post_id', sa.String(100), nullable=False, comment='ID único do post na plataforma de origem'),
        sa.Column('conteudo', sa.Text(), nullable=True, comment='Conteúdo textual do post'),
        sa.Column('url_post', sa.Text(), nullable=True, comment='URL direta para o post na rede social'),
        sa.Column('data_postagem', sa.DateTime(timezone=True), nullable=True, comment='Data e hora em que o post foi publicado'),
        sa.Column('curtidas', sa.Integer(), nullable=True, default=0, comment='Número de curtidas/reactions do post'),
        sa.Column('comentarios', sa.Integer(), nullable=True, default=0, comment='Número de comentários no post'),
        sa.Column('compartilhamentos', sa.Integer(), nullable=True, default=0, comment='Número de compartilhamentos do post'),
        sa.Column('visualizacoes', sa.Integer(), nullable=True, default=0, comment='Número de visualizações do post'),
        sa.Column('tipo_conteudo', sa.String(20), nullable=True, comment="Tipo de conteúdo ('texto', 'imagem', 'video', 'link', etc.)"),
        sa.Column('url_imagem', sa.Text(), nullable=True, comment='URL da imagem em anexo ao post'),
        sa.Column('url_video', sa.Text(), nullable=True, comment='URL do vídeo em anexo ao post'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Data de criação do registro'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False, comment='Data de atualização do registro'),
        sa.CheckConstraint('clube_id IS NOT NULL OR jogador_id IS NOT NULL', name='ck_posts_redes_sociais_dono'),
        sa.UniqueConstraint('rede_social', 'post_id', name='uq_post_rede_social'),
        comment='Armazena posts de redes sociais de clubes e jogadores'
    )
    
    # Create indexes
    op.create_index('idx_posts_redes_sociais_clube', 'posts_redes_sociais', ['clube_id'])
    op.create_index('idx_posts_redes_sociais_jogador', 'posts_redes_sociais', ['jogador_id'])
    op.create_index('idx_posts_redes_sociais_rede', 'posts_redes_sociais', ['rede_social'])
    op.create_index('idx_posts_redes_sociais_data', 'posts_redes_sociais', ['data_postagem'])

def downgrade():
    # Drop the table and all its dependencies
    op.drop_constraint('uq_post_rede_social', 'posts_redes_sociais', type_='unique')
    op.drop_constraint('ck_posts_redes_sociais_dono', 'posts_redes_sociais', type_='check')
    op.drop_index('idx_posts_redes_sociais_data', table_name='posts_redes_sociais')
    op.drop_index('idx_posts_redes_sociais_rede', table_name='posts_redes_sociais')
    op.drop_index('idx_posts_redes_sociais_jogador', table_name='posts_redes_sociais')
    op.drop_index('idx_posts_redes_sociais_clube', table_name='posts_redes_sociais')
    op.drop_table('posts_redes_sociais')
