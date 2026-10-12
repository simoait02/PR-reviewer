"""add parent-child chunks and remove unused document fields

Revision ID: c41f0b7e8d2a
Revises: a18d6e4f2b7c
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c41f0b7e8d2a"
down_revision: str | Sequence[str] | None = "a18d6e4f2b7c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


CATEGORIES = (
    "ARCHITECTURE",
    "CODE_QUALITY",
    "CODE_REVIEW",
    "COLLABORATION",
    "DELIVERY_AND_OPERATIONS",
    "DEPENDENCIES_AND_SUPPLY_CHAIN",
    "DOCUMENTATION_AND_TEAM_PRACTICES",
    "OBSERVABILITY_AND_RELIABILITY",
    "PROJECT_MANAGEMENT",
    "PROJECT_READINESS",
    "REQUIREMENTS_AND_PLANNING",
    "SECURITY_AND_PRIVACY",
    "TESTING",
)


def upgrade() -> None:
    op.drop_column("documents", "description")
    op.drop_column("documents", "category")
    op.execute("DROP TYPE IF EXISTS category")

    op.add_column(
        "chunks",
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_chunks_parent_id",
        "chunks",
        "chunks",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_chunks_parent_id",
        "chunks",
        ["parent_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_chunks_parent_id", table_name="chunks")
    op.drop_constraint(
        "fk_chunks_parent_id",
        "chunks",
        type_="foreignkey",
    )
    op.drop_column("chunks", "parent_id")

    category_enum = postgresql.ENUM(*CATEGORIES, name="category")
    category_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "documents",
        sa.Column(
            "description",
            sa.String(),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "documents",
        sa.Column(
            "category",
            category_enum,
            nullable=False,
            server_default="CODE_QUALITY",
        ),
    )
    op.alter_column(
        "documents",
        "description",
        server_default=None,
    )
    op.alter_column(
        "documents",
        "category",
        server_default=None,
    )
