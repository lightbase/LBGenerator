import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer, String, DateTime, Binary, Boolean
from sqlalchemy.schema import Sequence
from sqlalchemy.schema import MetaData
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class LB_Base(Base):

    __tablename__ = 'lb_base'

    id_base = Column(Integer, primary_key=True)
    nome_base = Column(String, nullable=False)
    json_base = Column(String, nullable=False)
    reg_model = Column(String, nullable=False)
    dt_base = Column(DateTime, nullable=False)

    password = Column(String, nullable=False)
    index_export = Column(Boolean, nullable=False)
    index_url = Column(String)
    index_time = Column(Integer)
    doc_extract = Column(Boolean, nullable=False)
    extract_time = Column(Integer)

class LB_Users(Base):

    __tablename__ = 'lb_users'

    id_user = Column(Integer, primary_key=True)
    nm_user = Column(String(10), nullable=False, unique=True)
    email_user = Column(String, unique=True)
    passwd_user = Column(String, nullable=False)
    js_auth = Column(String, nullable=False)
    dt_cad = Column(DateTime, nullable=False)
    in_active = Column(Boolean, nullable=False)

class LB_Form(Base):

    __tablename__ = 'lb_form'

    id_form = Column(Integer, primary_key=True)
    id_base = Column(Integer, ForeignKey('lb_base.id_base'), nullable=False)
    nome_form = Column(String)
    xml_form = Column(String)
    html_form = Column(String)

class RegSuperClass():
    def __init__(self, id_reg, json_reg, grupos_acesso=None, dt_reg=None, dt_last_up=None, dt_reg_del=None,
            dt_index_rel=None, dt_index_tex=None, dt_index_sem=None, **kwargs):
        self.id_reg = id_reg
        self.json_reg = json_reg
        self.grupos_acesso = grupos_acesso
        self.dt_reg = dt_reg
        self.dt_last_up = dt_last_up
        self.dt_reg_del = dt_reg_del
        self.dt_index_rel = dt_index_rel
        self.dt_index_tex = dt_index_tex
        self.dt_index_sem = dt_index_sem
        for k in kwargs:
            if isinstance(kwargs[k], list) and all(v is None for v in kwargs[k]):
                # Set value to None if is an empty list
                kwargs[k]= None
            elif kwargs[k] == '':
                kwargs[k]= None
        self.__dict__.update(kwargs)


def get_reg_table(base_name, metadata, **rel_fields):
    cols = (
        'lb_reg_%s' %(base_name), MetaData(),
        Column('id_reg', Integer, Sequence('lb_reg_%s_id_reg_seq' %(base_name)), primary_key=True),
        Column('json_reg', String, nullable=False),
        Column('grupos_acesso', String),#nullable=False
        Column('dt_reg', DateTime, nullable=False),
        Column('dt_last_up', DateTime, nullable=False),
        Column('dt_reg_del', DateTime),
        Column('dt_index_rel', DateTime),
        Column('dt_index_tex', DateTime),
        Column('dt_index_sem', DateTime),
    )

    TYPE_MAPPING = {
        'Text':            sqlalchemy.types.String,
        #'Document':       sqlalchemy.types.String,
        'Integer':         sqlalchemy.types.Integer,
        'Decimal':         sqlalchemy.types.Float,
        'Money':           sqlalchemy.types.Float,
        'SelfEnumerated':  sqlalchemy.types.Integer,
        'DateTime':        sqlalchemy.types.DateTime,
        'Date':            sqlalchemy.types.Date,
        'Time':            sqlalchemy.types.Time,
        #'Image':          sqlalchemy.types.String,
        #'Sound':          sqlalchemy.types.String,
        #'Video':          sqlalchemy.types.String,
        'Url':             sqlalchemy.types.String,
        'Boolean':         sqlalchemy.types.Boolean,
        'TextArea':        sqlalchemy.types.String,
        #'File':           sqlalchemy.types.String,
        'Html':            sqlalchemy.types.String,
        'Email':           sqlalchemy.types.String,
        'Json':            sqlalchemy.types.String
    }

    include_columns = [ ]

    if rel_fields:
        for rel_field in rel_fields:
            field = rel_fields[rel_field]
            col_type = TYPE_MAPPING[field.datatype]
            if field.__dim__ > 0:
                # TODO: Fix NULL casing, this will help:
                #https://github.com/psycopg/psycopg2/blob/497247a52836e971b0b5a5779d0c5c60b98e654d/psycopg/adapter_list.c
                #https://github.com/zzzeek/sqlalchemy/blob/master/lib/sqlalchemy/dialects/postgresql/base.py
                #http://stackoverflow.com/questions/22485971/python-sqlalchemy-insert-array-postgres-with-null-values-not-possible
                #https://groups.google.com/forum/#!msg/sqlalchemy/D5N9L4Ihgt8/0is1EGS0798J
                col_type = ARRAY(col_type, dimensions=field.__dim__)
            unique = True if 'Unique' in field.indices else False
            custom_col = Column(rel_field, col_type, unique=unique)
            cols += (custom_col,)
            include_columns.append(rel_field)

    try: return Table(*cols, extend_existing=True, autoload=True, include_columns=include_columns)
    except: return Table(*cols, extend_existing=True)

class DocSuperClass():
    def __init__(self, id_doc, id_reg, nome_doc, blob_doc, mimetype,
            grupos_acesso=None, texto_doc=None, dt_ext_texto=None):
        self.id_doc = id_doc
        self.id_reg = id_reg
        self.grupos_acesso = grupos_acesso
        self.nome_doc = nome_doc
        self.blob_doc = blob_doc
        self.mimetype = mimetype
        self.texto_doc = texto_doc
        self.dt_ext_texto = dt_ext_texto

def get_doc_table(base_name, metadata):
    doc_table = Table(
        'lb_doc_%s' %(base_name), MetaData(),
        Column('id_doc', Integer, Sequence('lb_doc_%s_id_doc_seq' %(base_name)), primary_key=True),
        #Column('id_reg', Integer, ForeignKey('lb_reg_%s.id_reg' %(base_name)), nullable=False),
        Column('id_reg', Integer, nullable=False),
        Column('grupos_acesso', String),
        Column('nome_doc', String),
        Column('blob_doc', Binary),
        Column('mimetype', String),
        Column('texto_doc', String),
        Column('dt_ext_texto', DateTime),
        extend_existing=True,
    )
    return doc_table
