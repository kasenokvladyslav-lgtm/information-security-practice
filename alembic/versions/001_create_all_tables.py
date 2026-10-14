"""Create all eight application tables."""
from alembic import op
import sqlalchemy as sa
revision = "001_create_all_tables"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("groups", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(20), nullable=False), sa.Column("department", sa.String(100), nullable=False), sa.Column("year", sa.Integer(), nullable=False), sa.UniqueConstraint("name"))
    op.create_table("roles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(50), nullable=False), sa.Column("description", sa.Text()), sa.UniqueConstraint("name"))
    op.create_table("permissions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("description", sa.Text()), sa.UniqueConstraint("name"))
    op.create_table("subjects", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(150), nullable=False), sa.Column("credits", sa.Float(), nullable=False), sa.Column("semester", sa.Integer(), nullable=False))
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("username", sa.String(50), nullable=False), sa.Column("email", sa.String(100), nullable=False), sa.Column("full_name", sa.String(150), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean()), sa.Column("created_at", sa.DateTime()), sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id")), sa.UniqueConstraint("username"), sa.UniqueConstraint("email"))
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("grades", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id"), nullable=False), sa.Column("grade", sa.Integer(), nullable=False), sa.Column("comment", sa.String(500)), sa.Column("date_assigned", sa.DateTime()), sa.Column("assigned_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False))
    op.create_table("user_roles", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True), sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), primary_key=True))
    op.create_table("role_permissions", sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), primary_key=True), sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permissions.id"), primary_key=True))

def downgrade():
    for name in ("role_permissions", "user_roles", "grades", "users", "subjects", "permissions", "roles", "groups"):
        op.drop_table(name)
