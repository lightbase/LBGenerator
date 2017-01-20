import datetime
import logging
from sqlalchemy.util import KeyedTuple
from alembic.migration import MigrationContext
from alembic.operations import Operations

from liblightbase.lbutils.conv import json2base
from . import CustomContextFactory
from ..entities import *
from ..index import Index
from ... import model
from ... import config
from ...lib import utils
from sqlalchemy.util import KeyedTuple
import requests

from pyramid.testing import DummyRequest
from .document import DocumentContextFactory
from ...views.document import DocumentCustomView

log = logging.getLogger()


class BaseContextFactory(CustomContextFactory):

    """ Base Factory Methods
    """
    entity = LBBase
     # Restarta o lbindex quando a base for modificada
    def lbirestart(self):
        param = {'directive': 'restart'}
        url = config.LBI_URL
        try:
            requests.post(url, data=param,timeout=(0.500))
        except (requests.exceptions.RequestException,
            requests.exceptions.ConnectionError) as e:
            print(e)
  
    def get_next_id(self):
        return model.base_next_id()

    def get_member(self, base):
        self.single_member = True
        member = self.session.query(self.entity)\
            .filter_by(name=base).first()
        return member or None

    def create_member(self, data):

        # Create reg and doc tables.
        base_name = data['name']
        base_json = utils.json2object(data['struct'])
        idx = data['idx_exp']

        '''
        Trata-se de uma variável global de __init__.py
        global BASES
        BASES = BaseMemory(begin_session, LBBase)
        '''
        base = model.BASES.set_base(base_json)
        data['struct'] = base.json
        data['txt_mapping'] = base.txt_mapping_json

        file_table = get_file_table(base_name, config.METADATA)
        doc_table = get_doc_table(base_name, config.METADATA,
            **base.relational_fields)
        file_table.create(config.ENGINE, checkfirst=True)
        doc_table.create(config.ENGINE, checkfirst=True)

        member = self.entity(**data)
        self.session.add(member)
        # Now commits and closes session in the view instead of here
        # flush() pushes operations to DB's buffer - DCarv
        self.session.flush()
        
        if idx:
            self.lbirestart()
        return member

    def update_member(self, id, data):
        member = self.get_member(id)
        if member is None:
            return None

        # NOTE: BaseContext's init method sets its base to the base
        # struct contained in the request, so we need to reset it here
        # to the base struct that is actually in the database - DCarv
        
        # remove base struct from cache
        model.BASES.bases.pop(member.name)
        # set old base struct as active
        self.set_base(member.struct)

        # check for base content changes
        old_base = json2base(member.struct)
        new_base = json2base(data['struct'])

        # list all fields that should be deleted
        del_cols = []
        for old_col_name, old_col in old_base.content.__allstructs__.items():
            if old_col_name not in new_base.content.__allsnames__:
                del_cols.append(old_col)

        # if any field will be deleted, delete it from all documents in the base
        if len(del_cols) > 0:
            # create a fake request for DocumentCustomView and DocumentContext
            url = "/%s/doc&$$={\"limit\":null}" % new_base.metadata.name
            for col in del_cols:
                params = {
                    'path': "[{\"path\":\"%s\",\"fn\":null,\"mode\":\"delete\",\"args\":[]}]" % ("/".join(col.path))
                }
                request = DummyRequest(path=url, params=params)
                request.method = 'PUT'
                request.matchdict = {"base": new_base.metadata.name}
                doc_view = DocumentCustomView(DocumentContextFactory(request), request)
                doc_view.update_collection()

        # check for relation field changes (to ALTER table if needed)
        old_doc_table = get_doc_table(old_base.metadata.name, config.METADATA,
            **old_base.relational_fields)
        new_doc_table = get_doc_table(new_base.metadata.name, config.METADATA,
            **new_base.relational_fields)

        # list relational fields that should be deleted
        del_cols = []
        for old_col in old_doc_table.columns:
            if old_col.name not in new_doc_table.columns:
                del_cols.append(old_col)

        # list relational fields that should be added
        new_cols = []
        for new_col in new_doc_table.columns:
            if new_col.name not in old_doc_table.columns:
                # Get liblightbase.lbbase.fields object.
                field = new_base.relational_fields[new_col.name]
                custom_col = get_custom_column(field)
                new_cols.append(custom_col)

        # create alembic connection and operation object
        db_conn = config.ENGINE.connect()
        alembic_ctx = MigrationContext.configure(db_conn)
        alembic_op = Operations(alembic_ctx)

        # drop columns
        for col in del_cols:
            alembic_op.drop_column(new_doc_table.name, col.name)

        # TODO: new_col cannot be required

        # add columns
        for col in new_cols:
            alembic_op.add_column(new_doc_table.name, col)

        # TODO: alter columns ?

        db_conn.close()

        # check for base name change
        if member.name != data['name']:
            old_name = 'lb_doc_%s' %(member.name)
            new_name = 'lb_doc_%s' %(data['name'])
            self.session.execute('ALTER TABLE %s RENAME TO %s' %(old_name, new_name))

            old_name = 'lb_file_%s' %(member.name)
            new_name = 'lb_file_%s' %(data['name'])
            self.session.execute('ALTER TABLE %s RENAME TO %s' %(old_name, new_name))

            old_name = 'lb_doc_%s_id_doc_seq' %(member.name)
            new_name = 'lb_doc_%s_id_doc_seq' %(data['name'])
            self.session.execute('ALTER SEQUENCE %s RENAME TO %s' %(old_name, new_name))

        # this will add any new fields to the base struct
        for name in data:
            setattr(member, name, data[name])

        # Now commits and closes session in the view instead of here
        # flush() pushes operations to DB's buffer - DCarv
        self.session.flush()

        model.HISTORY.create_member(**{
            'id_base': member.id_base,
            'author': 'Author',
            'date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'name': member.name,
            'structure': utils.json2object(member.struct),
            'status': 'UPDATED'
        })
    
        self.lbirestart()

        # remove base struct from cache
        model.BASES.bases.pop(member.name)

        return member

    def delete_member(self, id):
        member = self.get_member(id)
        if member is None:
            return None

        index = None
        relational_fields = model.BASES.get_base(member.name).relational_fields
        if model.BASES.bases.get(member.name) is not None:
            index = Index(model.BASES.bases[member.name], None)
            del model.BASES.bases[member.name]
        idx = member.idx_exp
        # Delete parallel tables.
        file_table = get_file_table(member.name, config.METADATA)
        doc_table = get_doc_table(member.name, config.METADATA, **relational_fields)
        file_table.drop(config.ENGINE, checkfirst=True)
        doc_table.drop(config.ENGINE, checkfirst=True)
        
        # Delete base.
        self.session.delete(member)
        # Now commits and closes session in the view instead of here
        # flush() pushes operations to DB's buffer - DCarv
        self.session.flush()

        if index:
            index.delete_root()

        model.HISTORY.create_member(**{
            'id_base': member.id_base,
            'author': 'Author',
            'date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'name': member.name,
            'structure': utils.json2object(member.struct),
            'status': 'DELETE'
        })
        
        if idx:
            self.lbirestart()
        return member

    def member_to_dict(self, member, fields=None):

        '''
        TODO: Não consegui entender pq o sempre verifica se há o método 
        "_asdict()" visto que ele nunca está disponível e o pior de tudo 
        é que sempre loga. Tá tosco no último e por essa razão comentei 
        a linha que gera o log! By Questor
        '''
        try:
            dict_member = member._asdict()
        except AttributeError as e:
            # Continue parsing.
            if not isinstance(member, KeyedTuple):
                member = self.member2KeyedTuple(member)

        dict_member = utils.json2object(member._asdict()['struct'])

        fields = getattr(self,'_query', {}).get('select')
        if fields and not '*' in fields:
            return {'metadata':
                {field: dict_member['metadata'][field] for field in fields}
            }

        return dict_member