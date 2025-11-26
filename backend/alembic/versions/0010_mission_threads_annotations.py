"""Add mission threads and map annotations"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0010_mission_threads_annotations"
down_revision = "0009_alert_geo_fields"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mission_threads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.add_column("incidents", sa.Column("mission_id", sa.Integer(), sa.ForeignKey("mission_threads.id"), nullable=True))

    op.create_table(
        "map_annotations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("annotation_type", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("radius_m", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("mission_threads.id"), nullable=True),
    )


def downgrade():
    op.drop_table("map_annotations")
    op.drop_column("incidents", "mission_id")
    op.drop_table("mission_threads")
