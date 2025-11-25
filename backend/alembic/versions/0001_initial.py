"""Initial schema for AEGIS-AI"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    userrole = sa.Enum(
        "citizen",
        "police",
        "medical",
        "fire",
        "admin",
        "command",
        name="userrole",
    )
    incidenttype = sa.Enum(
        "crime",
        "medical",
        "fire",
        "accident",
        "hazard",
        "unrest",
        "flood",
        "infrastructure",
        "crowd",
        "suspicious",
        "other",
        name="incidenttype",
    )
    incidentseverity = sa.Enum(
        "low", "medium", "high", "critical", name="incidentseverity"
    )
    incidentstatus = sa.Enum(
        "pending", "verified", "dispatched", "resolved", "false_alarm", name="incidentstatus"
    )
    unitstatus = sa.Enum("idle", "busy", "offline", name="unitstatus")

    # Enums must be created explicitly for Postgres
    userrole.create(op.get_bind(), checkfirst=True)
    incidenttype.create(op.get_bind(), checkfirst=True)
    incidentseverity.create(op.get_bind(), checkfirst=True)
    incidentstatus.create(op.get_bind(), checkfirst=True)
    unitstatus.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("email", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", userrole, nullable=False, server_default="citizen"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("callsign", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("unit_type", userrole, nullable=False),
        sa.Column("status", unitstatus, nullable=False, server_default="idle"),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), index=True, nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("incident_type", incidenttype, nullable=False, server_default="other"),
        sa.Column("severity", incidentseverity, nullable=False, server_default="low"),
        sa.Column("status", incidentstatus, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("reporter_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_unit_id", sa.Integer(), sa.ForeignKey("units.id"), nullable=True),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("severity", incidentseverity, nullable=False, server_default="low"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id"), nullable=True),
    )

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )


def downgrade():
    op.drop_table("comments")
    op.drop_table("alerts")
    op.drop_table("incidents")
    op.drop_table("units")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS unitstatus")
    op.execute("DROP TYPE IF EXISTS incidentstatus")
    op.execute("DROP TYPE IF EXISTS incidentseverity")
    op.execute("DROP TYPE IF EXISTS incidenttype")
    op.execute("DROP TYPE IF EXISTS userrole")
