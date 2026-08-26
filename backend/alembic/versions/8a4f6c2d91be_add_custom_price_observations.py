"""add isolated custom price observations

Revision ID: 8a4f6c2d91be
Revises: 1c3d9dad1ad0
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8a4f6c2d91be"
down_revision: Union[str, None] = "1c3d9dad1ad0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "custom_price_observations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.Column("supplier_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("contract_type", sa.String(length=32), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("data_quality", sa.String(length=16), nullable=True),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("custom_price_observations")
