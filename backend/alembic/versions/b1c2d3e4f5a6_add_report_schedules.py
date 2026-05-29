"""add report_schedules table

Revision ID: b1c2d3e4f5a6
Revises: a0bf4ea01bf5
Create Date: 2026-05-30 04:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'a0bf4ea01bf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'report_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('site_url', sa.String(length=512), nullable=False),
        sa.Column('frequency', sa.String(length=16), nullable=False),
        sa.Column('recipient', sa.String(length=255), nullable=False),
        sa.Column('brand_company', sa.String(length=255), nullable=True),
        sa.Column('brand_color', sa.String(length=16), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('report_schedules')
