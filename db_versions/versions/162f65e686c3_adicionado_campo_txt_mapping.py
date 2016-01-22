from alembic import op
import sqlalchemy as sa


"""adicionado campo txt_mapping

Revision ID: 162f65e686c3
Revises: 3ead0765bf0
Create Date: 2015-11-10 16:39:21.672950

"""

# revision identifiers, used by Alembic.
revision = '162f65e686c3'
down_revision = '3ead0765bf0'

def upgrade():
    op.execute('ALTER TABLE lb_base ADD COLUMN txt_mapping character varying;')
    pass


def downgrade():
    op.execute('ALTER TABLE lb_base DROP COLUMN txt_mapping;')
    pass
