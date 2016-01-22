from alembic import op
import sqlalchemy as sa


"""txt_index_n_mapping

Revision ID: 541f8046f693
Revises: 162f65e686c3
Create Date: 2015-11-17 15:53:34.319409

"""

# revision identifiers, used by Alembic.
revision = '541f8046f693'
down_revision = '162f65e686c3'

def upgrade():
    op.create_table(
        "lb_txt_idx",
        sa.Column("id_idx", sa.Integer(), nullable=False),
        sa.Column("nm_idx", sa.String(), nullable=False),
        sa.Column("cfg_idx", sa.String(), nullable=False),
        sa.Column("dt_crt_idx", sa.DateTime(), nullable=False),
        sa.Column("dt_upt_idx", sa.DateTime(), nullable=False),
        sa.Column("url_idx", sa.String(), nullable=False),
        sa.Column("actv_idx", sa.Boolean(), nullable=False),
        sa.Column("struct", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id_idx"),
        sa.UniqueConstraint("nm_idx"))

        # NOTE: Original SQL statement! By Questor
        # -- Table: lb_txt_idx

        # -- DROP TABLE lb_txt_idx;

        # -- Table: lb_txt_idx

        # -- DROP TABLE lb_txt_idx;

        # CREATE TABLE lb_txt_idx
        # (
          # id_idx serial NOT NULL,
          # nm_idx character varying NOT NULL,
          # cfg_idx character varying NOT NULL,
          # dt_crt_idx timestamp without time zone NOT NULL,
          # dt_upt_idx timestamp without time zone NOT NULL,
          # url_idx character varying NOT NULL,
          # actv_idx boolean NOT NULL,
          # struct character varying NOT NULL,
          # CONSTRAINT lb_txt_idx_id_pkey PRIMARY KEY (id_idx),
          # CONSTRAINT lb_txt_idx_nm_key UNIQUE (nm_idx)
        # )
        # WITH (
          # OIDS=FALSE
        # );
        # ALTER TABLE lb_txt_idx
          # OWNER TO postgres;
    pass


def downgrade():
    op.drop_table("lb_txt_idx")
    pass
