import sqlalchemy
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import sessionmaker, mapper
from lbgenerator.model.entities import *
from lbgenerator.lib.generator import BaseMemory
from sqlalchemy.schema import Sequence

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
    global BASES
    global index_url
    global _history
    global tmp_dir

    db_url = settings['sqlalchemy.url']
    index_url = settings['index.url']
    pool_size = int(settings['sqlalchemy.pool_size'])
    max_overflow = int(settings['sqlalchemy.max_overflow'])
    tmp_dir = settings['storage.tmp_dir']

    engine = create_engine(db_url, pool_size=pool_size, max_overflow=max_overflow)
    metadata = MetaData(engine)
    BASES = BaseMemory(begin_session, LB_Base)

    lb_base = LB_Base.__table__
    metadata.create_all(bind=engine, tables=[lb_base])

    from lbgenerator.model.metabase import HistoryMetaBase
    _history = HistoryMetaBase()
    _history.create_base(begin_session)

def reg_hyper_class(base_name, **custom_cols):
    """ Sqla's dynamic mapp (reg table)
    """
    classname = 'LB_Reg_%s' %(base_name)
    reg_table = get_reg_table(base_name, metadata, **custom_cols)

    def reg_next_id():
        """ Get next value from sequence.
        """
        seq = Sequence('lb_reg_%s_id_reg_seq' %(base_name))
        seq.create(bind=engine)
        session = begin_session()
        _next = session.execute(seq)
        session.close()
        return _next

    ext = {
        'next_id': reg_next_id,
        'base_name': base_name
    }

    RegHyperClass = type(classname, (RegSuperClass, ), ext)
    mapper(RegHyperClass, reg_table)
    return RegHyperClass

def doc_hyper_class(base_name):
    """ Sqla's dynamic mapp (doc table)
    """
    classname = 'LB_Doc_%s' %(base_name)
    doc_table = get_doc_table(base_name, metadata)

    def doc_next_id():
        """ Get next value from sequence.
        """
        seq = Sequence('lb_doc_%s_id_doc_seq' %(base_name))
        seq.create(bind=engine)
        session = begin_session()
        _next = session.execute(seq)
        session.close()
        return _next

    ext = {
        'next_id': doc_next_id,
        'base_name': base_name
    }

    DocHyperClass = type(classname, (DocSuperClass, ), ext)
    mapper(DocHyperClass, doc_table)
    return DocHyperClass

