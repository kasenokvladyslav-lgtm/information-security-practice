"""Drop plaintext email after encrypted migration"""
from alembic import op
import sqlalchemy as sa
revision = 'zpr2_pii_drop'
down_revision = 'zpr2_pii_add'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    left = conn.execute(sa.text('SELECT COUNT(*) FROM users WHERE encrypted_email IS NULL OR email_index IS NULL')).scalar()
    if left:
        raise RuntimeError(f'{left} users not migrated: refusing to drop plaintext email')
    with op.batch_alter_table('users') as batch:
        batch.drop_index('ix_users_email')
        batch.drop_column('email')

def downgrade():
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('email',sa.String(100),nullable=True))
        batch.create_index('ix_users_email',['email'],unique=True)
