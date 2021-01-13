from sqlalchemy.sql import table, column
from sqlalchemy import String
from alembic import op
#import sqlalchemy as sa

"""create api_key column on table lb_doc__user

Revision ID: 24f52aba320
Revises: 3ead0765bf0
Create Date: 2015-08-05 18:01:09.946168

"""

# revision identifiers, used by Alembic.
revision = '24f52aba320'
down_revision = '541f8046f693'


def upgrade():
    op.execute('ALTER TABLE lb_doc__user ADD COLUMN api_key character varying(200);')
    #op.execute(' TABLE lb_doc__user DROP COLUMN status_user;')


    #For old version
    #op.execute('ALTER TABLE lb_doc__user DROP COLUMN id_user;')
    #op.execute('ALTER TABLE lb_doc__user DROP COLUMN email_user;')
    #op.execute('ALTER TABLE lb_doc__user DROP COLUMN name_base;')
    #op.execute('ALTER TABLE lb_doc__user DROP COLUMN creation_date_user;')
    #op.execute('ALTER TABLE lb_doc__user DROP COLUMN status_user;')
    #op.execute('ALTER TABLE lb_doc__user ADD COLUMN id_user character varying(200);')
    
    account = table('lb_base',
      	column('name', String)
    )
    op.execute(
     	account.delete().\
         	where(account.c.name==op.inline_literal('_user'))
    )
    pass

   
def downgrade():
    op.execute('ALTER TABLE lb_doc__user DROP COLUMN api_key;')
    pass

