"""Add idempotency_key column to payments table.

Revision ID: 002
Revises: 001
Create Date: 2024-12-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_add_idempotency_key"
down_revision: Union[str, None] = "001_initial_payment_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add idempotency_key column with unique index."""
    op.add_column(
        "payments",
        sa.Column("idempotency_key", sa.String(255), nullable=True),
    )

    # Create unique index for idempotency key
    op.create_index(
        "ix_payments_idempotency_key",
        "payments",
        ["idempotency_key"],
        unique=True,
    )


def downgrade() -> None:
    """Remove idempotency_key column."""
    op.drop_index("ix_payments_idempotency_key", table_name="payments")
    op.drop_column("payments", "idempotency_key")
