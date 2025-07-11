"""Initial clean migration

Revision ID: 2d2c7a6cc658
Revises: 
Create Date: 2025-06-14 18:38:08.413563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d2c7a6cc658'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('audit_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('action', sa.String(length=255), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contact_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('submitted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('inlog_gegevens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('voornaam', sa.String(length=100), nullable=True),
    sa.Column('achternaam', sa.String(length=100), nullable=True),
    sa.Column('telefoonnummer', sa.String(length=20), nullable=True),
    sa.Column('date_joined', sa.DateTime(), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('health_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('heart_rate', sa.Integer(), nullable=True),
    sa.Column('steps', sa.Integer(), nullable=True),
    sa.Column('sleep_hours', sa.Float(), nullable=True),
    sa.Column('stress_level', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['inlog_gegevens.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('health_data')
    op.drop_table('inlog_gegevens')
    op.drop_table('contact_message')
    op.drop_table('audit_log')
    # ### end Alembic commands ###
