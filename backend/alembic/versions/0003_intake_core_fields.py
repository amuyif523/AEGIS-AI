"""Add incident source, media, and audit fields"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0003_intake_core_fields"
down_revision = "0002_expand_roles"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        incident_source = postgresql.ENUM(
            "citizen",
            "responder",
            "ops_center",
            "sensor",
            "weather",
            "other",
            name="incidentsource",
        )
        incident_source.create(bind, checkfirst=True)
    else:
        incident_source = sa.Enum(
            "citizen", "responder", "ops_center", "sensor", "weather", "other", name="incidentsource"
        )

    op.add_column("incidents", sa.Column("source", incident_source, nullable=False, server_default="citizen"))
    op.add_column("incidents", sa.Column("media_url", sa.String(), nullable=True))
    op.add_column("incidents", sa.Column("media_type", sa.String(), nullable=True))
    op.add_column("incidents", sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("incidents", sa.Column("dispatched_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("incidents", sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("incidents", sa.Column("verified_by_id", sa.Integer(), nullable=True))
    op.add_column("incidents", sa.Column("dispatched_by_id", sa.Integer(), nullable=True))
    op.add_column("incidents", sa.Column("resolved_by_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "incidents", "users", ["verified_by_id"], ["id"])
    op.create_foreign_key(None, "incidents", "users", ["dispatched_by_id"], ["id"])
    op.create_foreign_key(None, "incidents", "users", ["resolved_by_id"], ["id"])


def downgrade():
    op.drop_constraint(None, "incidents", type_="foreignkey")
    op.drop_constraint(None, "incidents", type_="foreignkey")
    op.drop_constraint(None, "incidents", type_="foreignkey")
    op.drop_column("incidents", "resolved_by_id")
    op.drop_column("incidents", "dispatched_by_id")
    op.drop_column("incidents", "verified_by_id")
    op.drop_column("incidents", "resolved_at")
    op.drop_column("incidents", "dispatched_at")
    op.drop_column("incidents", "verified_at")
    op.drop_column("incidents", "media_type")
    op.drop_column("incidents", "media_url")
    op.drop_column("incidents", "source")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS incidentsource")
