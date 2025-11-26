"""Add AI triage risk fields"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0005_ai_triage_fields"
down_revision = "0004_verification_media"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("incidents", sa.Column("ai_confidence", sa.Float(), nullable=True))
    op.add_column("incidents", sa.Column("escalation_probability", sa.Float(), nullable=True))
    op.add_column("incidents", sa.Column("spread_risk", sa.Float(), nullable=True))
    op.add_column("incidents", sa.Column("casualty_likelihood", sa.Float(), nullable=True))
    op.add_column("incidents", sa.Column("crowd_size_estimate", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("incidents", "crowd_size_estimate")
    op.drop_column("incidents", "casualty_likelihood")
    op.drop_column("incidents", "spread_risk")
    op.drop_column("incidents", "escalation_probability")
    op.drop_column("incidents", "ai_confidence")
