"""Add spatial risk index to incidents"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0008_spatial_risk_index"
down_revision = "0007_geometry_indexing"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("incidents", sa.Column("spatial_risk_index", sa.Float(), nullable=True))


def downgrade():
    op.drop_column("incidents", "spatial_risk_index")
