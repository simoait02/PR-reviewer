"""retire document categories

Revision ID: 9f4a2c7b1d6e
Revises: b62a5854a588
"""

from collections.abc import Sequence

revision: str = "9f4a2c7b1d6e"
down_revision: str | Sequence[str] | None = "b62a5854a588"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
