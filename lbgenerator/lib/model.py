from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker, object_mapper, clear_mappers


class Engine():
    engine = create_engine('postgresql://postgres@10.0.0.154/gerador_bases')
    session = sessionmaker(engine)()
    metadata = MetaData(engine)

    def get_conn(self):
        return Engine.engine, Engine.session, Engine.metadata

    def mapper_all(self, base_name):
        metadata = Engine.metadata
        tables = define_bases_table(metadata), define_forms_table(metadata), define_regs_table(base_name, metadata), define_docs_table(base_name, metadata)

        return tables

def map_class_to_table(cls, table, entity_name, **kw):
     newcls = type(entity_name, (cls, ), {})
     mapper(newcls, table, **kw)
     return newcls

class LB_bases(object):
    def __init__(self, id_base, nome_base, xml_base):
        self.id_base = id_base
        self.nome_base = nome_base
        self.xml_base = xml_base

class Bases_seq():
    def __init__(self):
        self.seq = Sequence('lb_bases_id_base_seq')

def define_bases_table(metadata):

    bases_table = Table(
                      'lb_bases', metadata,
                      Column('id_base', Integer, primary_key=True),
                      Column('nome_base', String()),
                      Column('xml_base', Text()),
                      extend_existing=True
                      )

    try: mapper(LB_bases, bases_table)
    except: mapper(LB_bases, bases_table, non_primary=True)
    return bases_table

class LB_forms(object):
    def __init__(self, id_form, id_base, nome_form, xml_form, html_form):
        self.id_form = id_form
        self.id_base = id_base
        self.nome_form = nome_form
        self.xml_form = xml_form
        self.html_form = html_form

class Forms_seq():
    def __init__(self):
        self.seq = Sequence('lb_forms_id_form_seq')

def define_forms_table(metadata):

    forms_table = Table(
                      'lb_forms', metadata,
                      Column('id_form', Integer, primary_key=True),
                      Column('id_base', Integer, ForeignKey('lb_bases.id_base')),
                      Column('nome_form', String()),
                      Column('xml_form', String()),
                      Column('html_form', String()),
                      extend_existing=True
                      )

    try: mapper(LB_forms, forms_table)
    except: mapper(LB_forms, forms_table, non_primary=True)
    return forms_table

class LB_regs(object):
    def __init__(self, id_reg, xml_reg, json_reg):
        self.id_reg = id_reg
        self.xml_reg = xml_reg
        self.json_reg = json_reg

class Regs_seq():
    def __init__(self, base_name):
        self.seq = Sequence('lb_regs_%s_id_reg_seq' %(base_name))

def define_regs_table(base_name, metadata):

    regs_table = Table(
                      'lb_regs_%s' %(base_name), metadata,
                      Column('id_reg', Integer, primary_key=True),
                      Column('xml_reg', String()),
                      Column('json_reg', String()),
                      extend_existing=True
                      )

    try: mapper(LB_regs, regs_table)
    except: mapper(LB_regs, regs_table, non_primary=True)
    return regs_table


class LB_docs(object):
    def __init__(self, id_doc, id_reg, nome_doc, blob, mimetype):
        self.id_doc = id_doc
        self.id_reg = id_reg
        self.nome_doc = nome_doc
        self.blob = blob
        self.mimetype = mimetype

class Docs_seq():
    def __init__(self, base_name):
        self.seq = Sequence('lb_docs_%s_id_doc_seq' %(base_name))

def define_docs_table(base_name, metadata):

    docs_table = Table(
                      'lb_docs_%s' %(base_name), metadata,
                      Column('id_doc', Integer, primary_key=True),
                      Column('id_reg', Integer, ForeignKey('lb_regs_%s.id_reg' %(base_name))),
                      Column('nome_doc', String()),
                      Column('blob', Binary),
                      Column('mimetype', String()),
                      extend_existing=True
                      )

    try: mapper(LB_docs, docs_table)
    except: mapper(LB_docs, docs_table, non_primary=True)
    return docs_table



