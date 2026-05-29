"""add local seo tables (businesses, citations, reviews)

Revision ID: a0bf4ea01bf5
Revises: e3ff7fe3c6e1
Create Date: 2026-05-30 03:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0bf4ea01bf5'
down_revision: Union[str, Sequence[str], None] = 'e3ff7fe3c6e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'local_businesses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.String(length=512), nullable=False),
        sa.Column('phone', sa.String(length=64), nullable=False),
        sa.Column('website', sa.String(length=512), nullable=True),
        sa.Column('gbp_place_id', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'citations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=128), nullable=False),
        sa.Column('url', sa.String(length=1024), nullable=True),
        sa.Column('listed_name', sa.String(length=255), nullable=False),
        sa.Column('listed_address', sa.String(length=512), nullable=False),
        sa.Column('listed_phone', sa.String(length=64), nullable=False),
        sa.Column('nap_consistent', sa.Boolean(), nullable=False),
        sa.Column('mismatch_fields', sa.Text(), nullable=True),
        sa.Column('last_checked', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['local_businesses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_citations_business_id', 'citations', ['business_id'])
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=128), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('suggested_response', sa.Text(), nullable=True),
        sa.Column('responded', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['local_businesses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_reviews_business_id', 'reviews', ['business_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_reviews_business_id', table_name='reviews')
    op.drop_table('reviews')
    op.drop_index('ix_citations_business_id', table_name='citations')
    op.drop_table('citations')
    op.drop_table('local_businesses')
