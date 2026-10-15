"""Add 5W audit log"""
from alembic import op
import sqlalchemy as sa
revision='zpr2_audit_log'
down_revision='zpr2_pii_drop'
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('audit_log',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('user_id',sa.Integer(),nullable=True),
        sa.Column('username',sa.String(50),nullable=True),
        sa.Column('ip_address',sa.String(45),nullable=False),
        sa.Column('action',sa.String(50),nullable=False),
        sa.Column('resource',sa.String(100),nullable=True),
        sa.Column('timestamp',sa.DateTime(),nullable=False),
        sa.Column('http_method',sa.String(10),nullable=True),
        sa.Column('endpoint',sa.String(200),nullable=True),
        sa.Column('status',sa.String(20),nullable=False),
        sa.Column('status_code',sa.Integer(),nullable=True),
        sa.Column('details',sa.Text(),nullable=True))
    op.create_index('ix_audit_log_action','audit_log',['action'])
    op.create_index('ix_audit_log_timestamp','audit_log',['timestamp'])
def downgrade():
    op.drop_index('ix_audit_log_timestamp',table_name='audit_log')
    op.drop_index('ix_audit_log_action',table_name='audit_log')
    op.drop_table('audit_log')
