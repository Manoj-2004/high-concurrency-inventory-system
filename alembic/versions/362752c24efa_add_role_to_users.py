"""Add role to users

Revision ID: 362752c24efa
Revises: 2567d65b8d5b
Create Date: 2026-07-03 00:17:13.971368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '362752c24efa'
down_revision: Union[str, Sequence[str], None] = '2567d65b8d5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE userrole AS ENUM ('CUSTOMER', 'ADMIN')")

    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role
        TYPE userrole
        USING role::userrole
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role
        TYPE VARCHAR(20)
    """)

    op.execute("DROP TYPE userrole")
