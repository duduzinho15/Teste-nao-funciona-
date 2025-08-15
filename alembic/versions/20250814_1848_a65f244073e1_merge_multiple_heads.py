"""Merge multiple heads

Revision ID: a65f244073e1
Revises: e80615e1f202, 20250809_1620, 20250809_1837, 20250810_0314
Create Date: 2025-08-14 18:48:01.455913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a65f244073e1'
down_revision = ('e80615e1f202', '20250809_1620', '20250809_1837', '20250810_0314')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
