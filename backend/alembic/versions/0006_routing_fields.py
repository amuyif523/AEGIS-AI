"""Add routing suggestion fields"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0006_routing_fields"
down_revision = "0005_ai_triage_fields"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("incidents", sa.Column("suggested_agencies", sa.String(), nullable=True))
    op.add_column("incidents", sa.Column("suggested_unit_type", sa.String(), nullable=True))
    op.add_column("incidents", sa.Column("routing_rationale", sa.String(), nullable=True))


def downgrade():
    op.drop_column("incidents", "routing_rationale")
    op.drop_column("incidents", "suggested_unit_type")
    op.drop_column("incidents", "suggested_agencies")
