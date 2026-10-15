"""Add encrypted PII columns"""
from alembic import op
import sqlalchemy as sa
revision = 'zpr2_pii_add'
down_revision = '001_create_all_tables'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('encrypted_email',sa.String(500),nullable=True))
        batch.add_column(sa.Column('email_index',sa.String(64),nullable=True))
        batch.add_column(sa.Column('encrypted_phone',sa.String(500),nullable=True))
        batch.create_index('ix_users_email_index',['email_index'],unique=True)

def downgrade():
    with op.batch_alter_table('users') as batch:
        batch.drop_index('ix_users_email_index')
        batch.drop_column('encrypted_phone')
        batch.drop_column('email_index')
        batch.drop_column('encrypted_email')
