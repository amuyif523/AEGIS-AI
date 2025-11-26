"""Add geo targeting fields to alerts"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0009_alert_geo_fields"
down_revision = "0008_spatial_risk_index"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("alerts", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("alerts", sa.Column("longitude", sa.Float(), nullable=True))
    op.add_column("alerts", sa.Column("radius_km", sa.Float(), nullable=True))
    op.add_column("alerts", sa.Column("recommended_action", sa.String(), nullable=True))
    op.add_column("alerts", sa.Column("audience", sa.String(), nullable=True))


def downgrade():
    op.drop_column("alerts", "audience")
    op.drop_column("alerts", "recommended_action")
    op.drop_column("alerts", "radius_km")
    op.drop_column("alerts", "longitude")
    op.drop_column("alerts", "latitude")
