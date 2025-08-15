"""Add UNIQUE constraint to clubes.nome

Revision ID: 20250810_0314
Revises: 3c958e4a60b7
Create Date: 2025-08-10 03:14:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250810_0314'
down_revision = '3c958e4a60b7'
branch_labels = None
depends_on = None

def upgrade():
    # Adiciona uma constraint UNIQUE à coluna 'nome' da tabela 'clubes'
    op.create_unique_constraint(
        'uq_clubes_nome',  # Nome da constraint
        'clubes',          # Nome da tabela
        ['nome']           # Coluna(s) que devem ser únicas
    )

def downgrade():
    # Remove a constraint UNIQUE da coluna 'nome' da tabela 'clubes'
    op.drop_constraint(
        'uq_clubes_nome',  # Nome da constraint
        'clubes',          # Nome da tabela
        type_='unique'     # Tipo da constraint
    )
