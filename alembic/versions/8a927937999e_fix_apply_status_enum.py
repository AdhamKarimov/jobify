"""fix apply status enum

Revision ID: 8a927937999e
Revises: edbbac389e17
Create Date: 2026-05-11 13:12:50.847202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a927937999e'
down_revision: Union[str, Sequence[str], None] = 'edbbac389e17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Avval enum type yaratish
    applystatus = sa.Enum('pending', 'accepted', 'rejected', name='applystatus')
    applystatus.create(op.get_bind())

    # Keyin column typini o'zgartirish
    op.alter_column('applies', 'status',
        existing_type=sa.VARCHAR(),
        type_=applystatus,
        existing_nullable=True,
        postgresql_using="status::applystatus"
    )

def downgrade() -> None:
    op.alter_column('applies', 'status',
        existing_type=sa.Enum('pending', 'accepted', 'rejected', name='applystatus'),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )
    op.execute("DROP TYPE applystatus")