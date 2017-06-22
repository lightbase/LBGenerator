from alembic import op
import sqlalchemy as sa


"""Initial neolight schema

Revision ID: 00000000000
Revises: None
Create Date: 2014-04-29 17:40:39

"""

# revision identifiers, used by Alembic
revision = '00000000000'
down_revision = None

def upgrade():
    # op.execute("CREATE SCHEMA brlight")
    # op.execute('SET search_path TO brlight, public')

    op.create_table('lb_base',
            sa.Column('id_base', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('struct', sa.String(), nullable=False),
            sa.Column('dt_base', sa.DateTime(), nullable=False),
            sa.Column('idx_exp', sa.Boolean(), nullable=False),
            sa.Column('idx_exp_url', sa.String(), nullable=True),
            sa.Column('idx_exp_time', sa.Integer(), nullable=True),
            sa.Column('file_ext', sa.Boolean(), nullable=False),
            sa.Column('file_ext_time', sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint('id_base')
    )

    op.create_table('lb_doc__history',
            sa.Column('id_doc', sa.Integer(), nullable=False),
            sa.Column('document', sa.String(), nullable=False),
            sa.Column('dt_doc', sa.DateTime(), nullable=False),
            sa.Column('dt_last_up', sa.DateTime(), nullable=False),
            sa.Column('dt_del', sa.DateTime(), nullable=True),
            sa.Column('dt_idx', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id_doc')
    )

    op.create_table('lb_doc__user',
            sa.Column('id_doc', sa.Integer(), nullable=False),
            sa.Column('document', sa.String(), nullable=False),
            sa.Column('dt_doc', sa.DateTime(), nullable=False),
            sa.Column('dt_last_up', sa.DateTime(), nullable=False),
            sa.Column('dt_del', sa.DateTime(), nullable=True),
            sa.Column('dt_idx', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id_doc')
    )


    op.create_table('lb_doc__form',
            sa.Column('id_doc', sa.Integer(), nullable=False),
            sa.Column('document', sa.String(), nullable=False),
            sa.Column('dt_doc', sa.DateTime(), nullable=False),
            sa.Column('dt_last_up', sa.DateTime(), nullable=False),
            sa.Column('dt_del', sa.DateTime(), nullable=True),
            sa.Column('dt_idx', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id_doc')
    )

    op.create_table('lb_doc__report',
            sa.Column('id_doc', sa.Integer(), nullable=False),
            sa.Column('document', sa.String(), nullable=False),
            sa.Column('dt_doc', sa.DateTime(), nullable=False),
            sa.Column('dt_last_up', sa.DateTime(), nullable=False),
            sa.Column('dt_del', sa.DateTime(), nullable=True),
            sa.Column('dt_idx', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id_doc')
    )

    op.create_table('lb_file__history',
            sa.Column('id_file', sa.Integer(), nullable=False),
            sa.Column('id_doc', sa.Integer(), nullable=False),
            sa.Column('filename', sa.String(), nullable=True),
            sa.Column('file', sa.dialects.postgresql.BYTEA(), nullable=True),
            sa.Column('mimetype', sa.String(), nullable=True),
            sa.Column('filetext', sa.String(), nullable=True),
            sa.Column('dt_ext_text', sa.DateTime(), nullable=True),
            sa.Column('filesize', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id_file')
    )

    op.create_table('lb_file__user',
            sa.Column('id_file', sa.Integer(), nullable=False),
            sa.Column('id_doc', sa.Integer(), nullable=False),
            sa.Column('filename', sa.String(), nullable=True),
            sa.Column('file', sa.dialects.postgresql.BYTEA(), nullable=True),
            sa.Column('mimetype', sa.String(), nullable=True),
            sa.Column('filetext', sa.String(), nullable=True),
            sa.Column('dt_ext_text', sa.DateTime(), nullable=True),
            sa.Column('filesize', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id_file')
    )

    op.create_table('lb_file__form',
            sa.Column('id_file', sa.Integer(), nullable=False),
            sa.Column('id_doc', sa.Integer(), nullable=False),
            sa.Column('filename', sa.String(), nullable=True),
            sa.Column('file', sa.dialects.postgresql.BYTEA(), nullable=True),
            sa.Column('mimetype', sa.String(), nullable=True),
            sa.Column('filetext', sa.String(), nullable=True),
            sa.Column('dt_ext_text', sa.DateTime(), nullable=True),
            sa.Column('filesize', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id_file')
    )

    op.create_table('lb_file__report',
            sa.Column('id_file', sa.Integer(), nullable=False),
            sa.Column('id_doc', sa.Integer(), nullable=False),
            sa.Column('filename', sa.String(), nullable=True),
            sa.Column('file', sa.dialects.postgresql.BYTEA(), nullable=True),
            sa.Column('mimetype', sa.String(), nullable=True),
            sa.Column('filetext', sa.String(), nullable=True),
            sa.Column('dt_ext_text', sa.DateTime(), nullable=True),
            sa.Column('filesize', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id_file')
    )

def downgrade():
    op.drop_table('lb_base')
    op.drop_table('lb_doc__history')
    op.drop_table('lb_doc__user')
    op.drop_table('lb_doc__form')
    op.drop_table('lb_doc__report')
    op.drop_table('lb_file__history')
    op.drop_table('lb_file__user')
    op.drop_table('lb_file__form')
    op.drop_table('lb_file__report')


