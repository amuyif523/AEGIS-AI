"""Expand UserRole enum for RBAC"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002_expand_roles"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

new_roles = [
    "traffic",
    "disaster_coordinator",
    "military_analyst",
    "national_supervisor",
    "verifier",
    "sys_admin",
]


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for role in new_roles:
            op.execute(
                f"ALTER TYPE userrole ADD VALUE IF NOT EXISTS '{role}'"
            )
    else:
        # SQLite: recreate enum via table recreation not needed; models will accept values
        pass


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # Downgrade for enums is not straightforward; document as no-op
        op.execute("-- downgrade of enum values is a no-op")
    else:
        pass
