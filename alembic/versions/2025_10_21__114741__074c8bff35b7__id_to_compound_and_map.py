"""id to compound and map

Revision ID: 074c8bff35b7
Revises: 23c41f647b1e
Create Date: 2025-10-21 11:47:41.322489

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "074c8bff35b7"
down_revision: Union[str, None] = "23c41f647b1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add the new id column (not as primary key yet)
    op.add_column("compounds", sa.Column("id", sa.Integer(), nullable=False))

    # Step 2: Find and drop the existing primary key constraint
    # First, let's check if there's an existing primary key constraint
    connection = op.get_bind()

    # Query to find the primary key constraint name
    result = connection.execute(
        sa.text(
            """
        SELECT conname 
        FROM pg_constraint 
        WHERE conrelid = 'compounds'::regclass 
        AND contype = 'p'
    """
        )
    )

    pk_constraint = result.fetchone()

    if pk_constraint:
        # Drop the existing primary key constraint
        op.drop_constraint(pk_constraint[0], "compounds", type_="primary")

    # Step 3: Now we can make 'name' nullable since it's no longer a primary key
    op.alter_column(
        "compounds", "name", existing_type=sa.VARCHAR(length=80), nullable=True
    )

    # Step 4: Create the new primary key constraint on 'id'
    op.create_primary_key("compounds_pkey", "compounds", ["id"])

    # Step 5: Create the unique constraint
    op.create_unique_constraint(
        "unique_compound_per_map", "compounds", ["map_id", "name"]
    )


def downgrade() -> None:
    # Reverse the operations in opposite order
    op.drop_constraint("unique_compound_per_map", "compounds", type_="unique")
    op.drop_constraint("compounds_pkey", "compounds", type_="primary")
    op.alter_column(
        "compounds", "name", existing_type=sa.VARCHAR(length=80), nullable=False
    )
    op.create_primary_key("compounds_pkey", "compounds", ["name"])
    op.drop_column("compounds", "id")
