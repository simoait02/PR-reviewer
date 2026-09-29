"""enforce one embedding per chunk

Revision ID: a18d6e4f2b7c
Revises: 9f4a2c7b1d6e
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a18d6e4f2b7c"
down_revision: str | Sequence[str] | None = "9f4a2c7b1d6e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_embeddings_chunk_id",
        "embeddings",
        ["chunk_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_embeddings_chunk_id",
        "embeddings",
        type_="unique",
    )
