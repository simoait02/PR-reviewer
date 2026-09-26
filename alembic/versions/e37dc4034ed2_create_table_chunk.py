"""create table chunk

Revision ID: e37dc4034ed2
Revises: 36db49e0221b
Create Date: 2026-09-25 17:07:14.581022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e37dc4034ed2'
down_revision: Union[str, Sequence[str], None] = '36db49e0221b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "chunks",
        sa.Column("id", postgresql.UUID, nullable=False, server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("document_id", postgresql.UUID, sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False), #foreign key
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("metadata", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("chunks")
    pass
