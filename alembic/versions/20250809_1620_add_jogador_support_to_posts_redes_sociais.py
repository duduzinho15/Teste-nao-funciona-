"""Add jogador support to posts_redes_sociais

Revision ID: 20250809_1620
Revises: 3c958e4a60b7
Create Date: 2025-08-09 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250809_1620'
down_revision = '3c958e4a60b7'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Tornar clube_id opcional
    with op.batch_alter_table('posts_redes_sociais', schema=None) as batch_op:
        batch_op.alter_column('clube_id',
                           existing_type=sa.INTEGER(),
                           nullable=True,
                           existing_comment='ID do clube dono do post')
    
    # 2. Adicionar coluna jogador_id
    with op.batch_alter_table('posts_redes_sociais', schema=None) as batch_op:
        batch_op.add_column(sa.Column('jogador_id', sa.Integer(), nullable=True, comment='ID do jogador dono do post'))
        batch_op.create_foreign_key('fk_posts_redes_sociais_jogador_id', 'jogadores', ['jogador_id'], ['id'], ondelete='CASCADE')
    
    # 3. Adicionar índice para jogador_id
    with op.batch_alter_table('posts_redes_sociais', schema=None) as batch_op:
        batch_op.create_index('idx_posts_redes_sociais_jogador', ['jogador_id'])
    
    # 4. Adicionar constraint para garantir que pelo menos um dos IDs (clube ou jogador) esteja preenchido
    op.execute("""
        ALTER TABLE posts_redes_sociais 
        ADD CONSTRAINT ck_posts_redes_sociais_owner 
        CHECK (clube_id IS NOT NULL OR jogador_id IS NOT NULL)
    """)
    
    # 5. Atualizar comentários das colunas
    op.alter_column('posts_redes_sociais', 'clube_id',
                   existing_type=sa.INTEGER(),
                   comment='ID do clube dono do post (opcional se jogador_id estiver preenchido)',
                   existing_nullable=True)
    
    op.alter_column('posts_redes_sociais', 'jogador_id',
                   existing_type=sa.INTEGER(),
                   comment='ID do jogador dono do post (opcional se clube_id estiver preenchido)',
                   existing_nullable=True)

def downgrade():
    # 1. Remover constraint de verificação
    with op.batch_alter_table('posts_redes_sociais', schema=None) as batch_op:
        batch_op.drop_constraint('ck_posts_redes_sociais_owner', type_='check')
    
    # 2. Remover chave estrangeira e índice de jogador_id
    with op.batch_alter_table('posts_redes_sociais', schema=None) as batch_op:
        batch_op.drop_constraint('fk_posts_redes_sociais_jogador_id', type_='foreignkey')
        batch_op.drop_index('idx_posts_redes_sociais_jogador')
    
    # 3. Remover a coluna jogador_id
    with op.batch_alter_table('posts_redes_sociais', schema=None) as batch_op:
        batch_op.drop_column('jogador_id')
    
    # 4. Tornar clube_id obrigatório novamente
    # Primeiro, garantir que não há linhas com clube_id nulo
    op.execute("UPDATE posts_redes_sociais SET clube_id = 0 WHERE clube_id IS NULL")
    
    with op.batch_alter_table('posts_redes_sociais', schema=None) as batch_op:
        batch_op.alter_column('clube_id',
                           existing_type=sa.INTEGER(),
                           nullable=False,
                           existing_comment='ID do clube dono do post')
