"""creating pgvector_extention

Revision ID: 1df5b2baa9c8
Revises:
Create Date: 2026-08-09 15:13:48.666393

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.

revision: str = "1df5b2baa9c8"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS vector")