"""Add geometry column and spatial index"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = "0007_geometry_indexing"
down_revision = "0006_routing_fields"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.add_column("incidents", sa.Column("geometry", Geometry(geometry_type="POINT", srid=4326)))
        op.execute("UPDATE incidents SET geometry = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_incidents_geom ON incidents USING GIST (geometry)")
    else:
        op.add_column("incidents", sa.Column("geometry", sa.String(), nullable=True))


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS idx_incidents_geom")
    op.drop_column("incidents", "geometry")
