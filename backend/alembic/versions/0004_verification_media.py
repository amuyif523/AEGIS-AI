"""Add verification/media/attachment fields"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0004_verification_media"
down_revision = "0003_intake_core_fields"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("incidents", sa.Column("flagged", sa.Integer(), server_default="0", nullable=False))
    op.add_column("incidents", sa.Column("flag_reason", sa.String(), nullable=True))
    op.add_column("incidents", sa.Column("duplicate_of_id", sa.Integer(), nullable=True))
    op.add_column("incidents", sa.Column("potential_duplicate_id", sa.Integer(), nullable=True))
    op.add_column("incidents", sa.Column("flagged_by_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "incidents", "users", ["flagged_by_id"], ["id"])
    op.create_foreign_key(None, "incidents", "incidents", ["duplicate_of_id"], ["id"])
    op.create_foreign_key(None, "incidents", "incidents", ["potential_duplicate_id"], ["id"])

    op.create_table(
        "incident_attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("media_type", sa.String(), nullable=True),
        sa.Column("metadata", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("incident_attachments")
    op.drop_constraint(None, "incidents", type_="foreignkey")
    op.drop_constraint(None, "incidents", type_="foreignkey")
    op.drop_constraint(None, "incidents", type_="foreignkey")
    op.drop_column("incidents", "flagged_by_id")
    op.drop_column("incidents", "potential_duplicate_id")
    op.drop_column("incidents", "duplicate_of_id")
    op.drop_column("incidents", "flag_reason")
    op.drop_column("incidents", "flagged")
