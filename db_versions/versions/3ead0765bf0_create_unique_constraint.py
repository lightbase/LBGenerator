"""create unique constraint

Revision ID: 3ead0765bf0
Revises: None
Create Date: 2014-08-05 15:40:39.459520

"""

# revision identifiers, used by Alembic.
revision = '3ead0765bf0'
down_revision = '00000000000' 

from alembic import op
#import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE lb_base ADD CONSTRAINT lb_base_name_key UNIQUE (name);')
    pass

def downgrade():
    op.execute('ALTER TABLE lb_base DROP CONSTRAINT lb_base_name_key;') 
    pass
