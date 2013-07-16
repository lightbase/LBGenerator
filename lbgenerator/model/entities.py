from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer, String, DateTime, Binary
from sqlalchemy.schema import Sequence

Base = declarative_base()

class LB_Base(Base):

    __tablename__ = 'lb_base'

    id_base = Column(Integer, primary_key=True)
    nome_base = Column(String, nullable=False)
    xml_base = Column(String)
    dt_base = Column(DateTime)

class LB_Form(Base):

    __tablename__ = 'lb_form'

    id_form = Column(Integer, primary_key=True)
    id_base = Column(Integer, ForeignKey('lb_base.id_base'), nullable=False)
    nome_form = Column(String)
    xml_form = Column(String)
    html_form = Column(String)

class RegSuperClass():
    def __init__(self, id_reg, json_reg, grupos_acesso=None, dt_reg=None, dt_reg_del=None,
            dt_index_rel=None, dt_index_tex=None, dt_index_sem=None, **kwargs):
        self.id_reg = id_reg
        self.json_reg = json_reg
        self.grupos_acesso = grupos_acesso
        self.dt_reg = dt_reg
        self.dt_reg_del = dt_reg_del
        self.dt_index_rel = dt_index_rel
        self.dt_index_tex = dt_index_tex
        self.dt_index_sem = dt_index_sem
        for k in kwargs:
            if kwargs[k] == '': kwargs[k]= None
        if kwargs: self.__dict__.update(kwargs)

def get_reg_table(base_name, metadata, **custom_cols):
    cols = (
        'lb_reg_%s' %(base_name), metadata,
        Column('id_reg', Integer, Sequence('lb_reg_%s_id_reg_seq' %(base_name)), primary_key=True),
        Column('json_reg', String, nullable=False),
        Column('grupos_acesso', String),#nullable=False
        Column('dt_reg', DateTime, nullable=False),
        Column('dt_reg_del', DateTime),
        Column('dt_index_rel', DateTime),
        Column('dt_index_tex', DateTime),
        Column('dt_index_sem', DateTime),
    )
    if custom_cols:
        for col in custom_cols['unique_cols']:
            if col in custom_cols['date_types']:
                cols += (Column(col, DateTime, unique=True),)
            else:
                cols += (Column(col, String, unique=True),)
        for col in custom_cols['normal_cols']:
            if col in custom_cols['date_types']:
                cols += (Column(col, DateTime),)
            else:
                cols += (Column(col, String),)
    return Table(*cols, extend_existing=True)

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
        'lb_doc_%s' %(base_name), metadata,
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
