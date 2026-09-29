"""update document categories

Revision ID: 9f4a2c7b1d6e
Revises: b62a5854a588
"""

from collections.abc import Sequence

from alembic import op

revision: str = "9f4a2c7b1d6e"
down_revision: str | Sequence[str] | None = "b62a5854a588"
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
    op.execute(
        "CREATE TYPE category_new AS ENUM ("
        + ", ".join(f"'{category}'" for category in CATEGORIES)
        + ")"
    )
    op.execute(
        "ALTER TABLE documents "
        "ALTER COLUMN category TYPE category_new "
        "USING category::text::category_new"
    )
    op.execute("DROP TYPE IF EXISTS category")
    op.execute("ALTER TYPE category_new RENAME TO category")


def downgrade() -> None:
    op.execute(
        "CREATE TYPE category_old AS ENUM ("
        "'BUG', 'SECURITY', 'PERFORMANCE', 'TESTING', 'ARCHITECTURE', "
        "'ERROR_HANDLING', 'CODE_STYLE', 'MAINTAINABILITY', 'DOCUMENTATION', "
        "'DATABASE', 'API'"
        ")"
    )
    op.execute(
        "ALTER TABLE documents "
        "ALTER COLUMN category TYPE category_old "
        "USING category::text::category_old"
    )
    op.execute("DROP TYPE category")
    op.execute("ALTER TYPE category_old RENAME TO category")
