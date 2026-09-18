"""add name column to sessions

Revision ID: a1b2c3d4e5f6
Revises: 9caba7aca993
Create Date: 2026-09-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '9caba7aca993'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default backfills any existing rows (e.g. if you don't wipe data
    # before running this); new sessions will always supply a real name via
    # the API, since CreateSessionRequest.name is required.
    op.add_column('sessions', sa.Column('name', sa.String(), nullable=False, server_default='Study Session'))


def downgrade() -> None:
    op.drop_column('sessions', 'name')
