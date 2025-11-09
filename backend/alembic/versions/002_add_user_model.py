"""Add User Model

Revision ID: 002_add_user_model
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_user_model'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create userrole enum
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'user', 'operator')")
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'user', 'operator', name='userrole'), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('telegram_id', sa.String(100), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_telegram_id', 'users', ['telegram_id'])
    
    # Update chats table to reference users
    # Note: assigned_to already exists in 001_initial, but we need to ensure the foreign key is correct
    op.create_foreign_key(
        'fk_chats_assigned_to_users',
        'chats',
        'users',
        ['assigned_to'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop foreign key
    op.drop_constraint('fk_chats_assigned_to_users', 'chats', type_='foreignkey')
    
    # Drop users table
    op.drop_table('users')
    
    # Drop enum
    op.execute("DROP TYPE IF EXISTS userrole")

