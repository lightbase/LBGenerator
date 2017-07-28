from sqlalchemy import event
from sqlalchemy.orm import mapper
from sqlalchemy.engine import Engine
from sqlalchemy.schema import Sequence
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import engine_from_config

from .. import config
from .entities import *
from ..lib.generator import BaseMemory
from ..lib.provider import AuthProvider
from .metabase.user import UserMetaBase
from .metabase.form import FormMetaBase
from .metabase.report import ReportMetaBase
from .metabase.search import SearchMetaBase
from .metabase.history import HistoryMetaBase

@event.listens_for(Engine, "connect")
def connect(dbapi_connection, connection_record):
    cursor=dbapi_connection.cursor()
    cursor.execute('set datestyle = "ISO, DMY";')
    cursor.close()

def begin_session():
    """ Returns Session object """

    session=scoped_session(
        sessionmaker(
            bind=config.ENGINE, 
            autocommit=True
        )
    )
    session.begin()
    return session

def make_restful_app():
    """ Initialize Restfull API.
    """

    global BASES
    global HISTORY
    global USER
    global FORM
    global REPORT 
    global SEARCH 

    # NOTE: Create Base Memory! John Doe
    BASES=BaseMemory(begin_session, LBBase)

    # NOTE: Create Base History stuff! John Doe
    HISTORY=HistoryMetaBase()
    HISTORY.create_base(begin_session)

    # NOTE: Create Base Users stuff! John Doe
    USER=UserMetaBase()
    USER.create_base(begin_session)

    # NOTE: Create Base Form stuff! John Doe
    FORM=FormMetaBase()
    FORM.create_base(begin_session)

    # NOTE: Create Base Report stuff! John Doe
    REPORT=ReportMetaBase()
    REPORT.create_base(begin_session)

    # NOTE: Create Base Report stuff! John Doe
    SEARCH=SearchMetaBase()
    SEARCH.create_base(begin_session)

    Sequence('lb_index_error_seq').create(bind=config.ENGINE)
    config.METADATA.create_all(bind=config.ENGINE,
        tables=[LBIndexError.__table__])

def base_next_id():
    """ Get next value from sequence
    """

    seq=Sequence('lb_base_id_base_seq')
    seq.create(bind=config.ENGINE)
    session=begin_session()
    _next=session.execute(seq)

    # TODO: Deveríamos fechar a sessão aqui uma vez que todas as views fecham
    # sessão ao final? By Questor
    session.close()

    return _next

def document_entity(base_name, next_id_fn=None, **custom_cols):
    """
    @param base_name: The base name to build a table object
    @return: Mapped entity, can be used for orm operations.

    Explicitly link a user defined class (LB_Doc_<base_name>)
    with table (lb_doc_<base_name>)
    """
    _table=get_doc_table(base_name, config.METADATA, **custom_cols)

    def _next_id():
        """ Get next value from sequence """
        seq=Sequence('lb_doc_%s_id_doc_seq' %(base_name))
        seq.create(bind=config.ENGINE)
        session=begin_session()
        _next=session.execute(seq)
        session.close()
        return _next

    class DocumentMappedEntity(LBDocument):
        __table__= _table
        if next_id_fn is not None:
            next_id=next_id_fn
        else:
            next_id=_next_id

    DocumentMappedEntity.__name__='LBDoc_%s' %(base_name)
    mapper(DocumentMappedEntity, _table)
    return DocumentMappedEntity

def file_entity(base_name):
    """
    @param base_name: The base name to build a table object
    @return: Mapped entity, can be used for orm operations.

    Explicitly link a user defined class (LB_File_<base_name>)
    with table (lb_file_<base_name>)
    """
    _table=get_file_table(base_name, config.METADATA)

    def _next_id():
        """ Get next value from sequence.
        """

        seq=Sequence('lb_file_%s_id_file_seq' %(base_name))
        seq.create(bind=config.ENGINE)
        session=begin_session()
        _next=session.execute(seq)
        session.close()
        return _next

    class FileMappedEntity(LBFile):
        __table__=_table
        next_id=_next_id

    FileMappedEntity.__name__='LBFile_%s' %(base_name)
    mapper(FileMappedEntity, _table)
    return FileMappedEntity

def user_callback(user_name, request):

    if user_name == config.ADMIN_USER:
        return 'Authenticated'

    owner=request.matchdict.get('owner')
    base=request.matchdict.get('base')
    resource=request.matchdict.get('id')
    auth_provider=AuthProvider(owner, base, resource)

    session=begin_session()
    user=session.query(LB_Users).filter_by(user_name=user_name).first()
    session.close()
    import json
    user_auth=json.loads(user.auth)

    for auth_pattern in user_auth:
        authorized=auth_provider.get_authorization(auth_pattern)
        if authorized: return authorized
    return []

