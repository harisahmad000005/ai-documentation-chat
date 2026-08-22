"""add users and document ownership

Revision ID: 398520ba67f0
Revises: e17caf196fbf
Create Date: 2026-08-22 23:09:57.808927

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "398520ba67f0"
down_revision: Union[str, Sequence[str], None] = "e17caf196fbf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create users table
    op.create_table(
        "users",
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Unique index for user email
    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )

    # Add updated_at to document chunks
    op.add_column(
        "document_chunks",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Add optional user ownership to documents
    op.add_column(
        "documents",
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    # Index user_id for faster document filtering
    op.create_index(
        op.f("ix_documents_user_id"),
        "documents",
        ["user_id"],
        unique=False,
    )

    # Foreign key: documents -> users
    op.create_foreign_key(
        "fk_documents_user_id_users",
        "documents",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove foreign key
    op.drop_constraint(
        "fk_documents_user_id_users",
        "documents",
        type_="foreignkey",
    )

    # Remove user_id index
    op.drop_index(
        op.f("ix_documents_user_id"),
        table_name="documents",
    )

    # Remove user_id from documents
    op.drop_column(
        "documents",
        "user_id",
    )

    # Remove updated_at from document_chunks
    op.drop_column(
        "document_chunks",
        "updated_at",
    )

    # Remove user email index
    op.drop_index(
        op.f("ix_users_email"),
        table_name="users",
    )

    # Remove users table
    op.drop_table("users")