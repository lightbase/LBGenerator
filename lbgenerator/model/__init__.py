import sqlalchemy
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import sessionmaker, mapper
from lbgenerator.model.entities import *
from lbgenerator.lib.generator import BaseContextObject

def begin_session():
    session = sessionmaker(bind=engine, autocommit=True)()
    session.begin()
    session.execute('SET datestyle = "ISO, DMY";')
    return session

def base_exists(base_name):
    if not base_name: 
        raise Exception('Missing param "nome_base"!')
    if base_name in get_bases(): 
        return True
    return False

def get_bases():
    """ Get all 'base_name' from LB_base
    """
    session = begin_session()
    bases = session.query(LB_Base.nome_base)
    session.close()
    return [base[0] for base in bases.all()]

def make_restful_app(**settings):
    """ Initialize Restfull App
    """
    global engine
    global metadata
    global base_context
    global index_url

    db_url = settings['sqlalchemy.url']
    index_url = settings['index.url']

    #engine = create_engine(db_url, poolclass=sqlalchemy.pool.NullPool)
    engine = create_engine(db_url)
    metadata = MetaData(engine)
    base_context = BaseContextObject(begin_session, LB_Base)

    lb_base = LB_Base.__table__
    metadata.create_all(bind=engine, tables=[lb_base])

def reg_hyper_class(base_name, **custom_cols):
    """ Sqla's dynamic mapp (reg table)
    """
    classname = 'LB_Reg_%s' %(base_name)
    reg_table = get_reg_table(base_name, metadata, **custom_cols)
    RegHyperClass = type(classname, (RegSuperClass, ), {})
    mapper(RegHyperClass, reg_table)
    return RegHyperClass

def doc_hyper_class(base_name):
    """ Sqla's dynamic mapp (doc table)
    """
    classname = 'LB_Doc_%s' %(base_name)
    doc_table = get_doc_table(base_name, metadata)
    DocHyperClass = type(classname, (DocSuperClass, ), {})
    mapper(DocHyperClass, doc_table)
    return DocHyperClass


