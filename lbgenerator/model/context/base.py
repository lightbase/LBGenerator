import datetime
import logging
import threading
from sqlalchemy.util import KeyedTuple
from alembic.migration import MigrationContext
from alembic.operations import Operations
from webob.acceptparse import Accept

from liblightbase.lbutils.conv import json2base
from liblightbase.lbutils.codecs import json2object
from liblightbase.lbbase.lbstruct.field import Field
from liblightbase.lbbase.lbstruct.group import Group
from liblightbase.lbbase.lbstruct.group import GroupMetadata
from liblightbase.lbbase.content import Content

from . import CustomContextFactory
from ..entities import *
from ..index import Index
from ... import model
from ... import config
from ...lib import utils
from ...lib import cache
from sqlalchemy.util import KeyedTuple
import requests

from pyramid.testing import DummyRequest
from .document import DocumentContextFactory
from ...views.document import DocumentCustomView
from ...lib.lbtasks import LBTaskManager

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

        # N >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.session.begin()
        self.session.commit()
        self.session.flush()
        self.session.close()
        # N <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # O >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Now commits and closes session in the view instead of here
        # flush() pushes operations to DB's buffer - DCarv
        # self.session.flush()
        # O <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

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

    def update_column_async(self, column_path, json_new_column,
                            id_user, user_agent, user_ip):
        # CREATE task
        task_name = 'update_column: %s' % ('/'.join(column_path))
        task_id, task_url = LBTaskManager()\
            .create(task_name, id_user, user_agent, user_ip, 0.0)

        worker_thread = threading.Thread(
            target=self.update_column,
            args=(column_path, json_new_column,),
            kwargs={'async': True, 'task_id': task_id}
        )
        worker_thread.start()

        return task_url

    def update_column(self, column_path, json_new_column,
                      async=False, task_id=None):
        """ Updates a column structure
        """
        if async:
            task_manager = LBTaskManager()

        try:
            dict_new_column = json2object(json_new_column)
            # new_column is either a Group or a Field (liblightbase.lbbase.lbstruct)
            new_column = self.object2content(dict_new_column)

            # base is a LBBase object
            base = self.get_base()
            member = self.get_member(base.metadata.name)
            if member is None:
                if async:
                    exc = Exception('Base not found: ' + base.metadata.name)
                    task_manager.on_error(task_id, exp)
                return None
            # base struct as dictionary
            dict_base = json2object(member.struct)
            # current_column is the Group/Field object before update
            current_column = base.get_struct(column_path[-1])
            if current_column.path != column_path:
                if async:
                    exc = Exception('Column not found: ' + '/'.join(column_path))
                    task_manager.on_error(task_id, exp)
                return None

            # check if the column's name was changed
            name_changed = False
            old_name = None
            if isinstance(current_column, Field) and isinstance(new_column, Field):
                if new_column.name != current_column.name:
                    old_name = current_column.name
                    current_column.name = new_column.name
                    name_changed = True
            elif isinstance(current_column, Group) and isinstance(new_column, Group):
                if new_column.metadata.name != current_column.metadata.name:
                    old_name = current_column.metadata.name
                    current_column.metadata.name = new_column.metadata.name
                    name_changed = True

            if name_changed:
                if async:
                    # update task progress
                    # TODO: log result if error
                    task_manager.on_update_progress(
                        task_id, 5.0, msg='Preparing to change column name')

                # get column value for each document
                url = '/%s/doc' % (base.metadata.name)
                search_param = '{"select":["id_doc", "%s"],"limit":null}' % column_path[-1]
                params = {
                    '$$': search_param
                }
                request = DummyRequest(path=url, params=params)
                request.method = 'GET'
                request.matchdict = {"base": base.metadata.name}
                request.accept = Accept("application/json")
                doc_view = DocumentCustomView(DocumentContextFactory(request), request)
                results = doc_view.get_collection(render_to_response=True)
                results = results.json_body['results']

                if async:
                    # update task progress
                    # TODO: log result if error
                    task_manager.on_update_progress(
                        task_id, 10.0, msg="Saved old documents' values")

                # delete old column value from documents
                url = "/%s/doc?$$={\"limit\":null}" % base.metadata.name
                json_path_list = '[{"path":"%s","fn":null,"mode":"delete","args":[]}]' % "/".join(column_path)
                params = {
                    'path': json_path_list,
                    'alter_files': False
                }
                request = DummyRequest(path=url, params=params)
                request.method = 'PUT'
                request.matchdict = {"base": base.metadata.name}
                doc_view = DocumentCustomView(DocumentContextFactory(request), request)
                doc_view.update_collection()

                if async:
                    # update task progress
                    # TODO: log result if error
                    task_manager.on_update_progress(
                        task_id, 20.0, msg='Deleted values in old column')

                # change base struct
                try:
                    current = dict_base
                    # traverse struct dict
                    for node in column_path:
                        if isinstance(current, dict) and current.get('content', None):
                            content_list = current['content']
                        else:
                            content_list = current

                        for f in content_list:
                            if f.get('field', None):
                                if f['field']['name'] == node:
                                    current = f
                                    break
                            elif f.get('group', None):
                                if f['group']['metadata']['name'] == node:
                                    current = f
                                    break

                    # current is a dictionary with current column struct
                    if current is None:
                        # undo delete column
                        self._undo_delete_column(base, old_name, column_path, results)
                        if async:
                            # TODO: better error message
                            exc = Exception('Column not found')
                            task_manager.on_error(task_id, exc)
                        return None

                    # get new name (Field or Group)
                    new_name = None
                    if current.get('field', None):
                        new_name = current_column.name
                        current['field']['name'] = new_name

                        # check if field is relational and change its name in postgres db
                        if current_column.is_rel:
                            self._alter_column_name(base, old_name, new_name)

                    elif current.get('group', None):
                        new_name = current_column.metadata.name
                        current['group']['metadata']['name'] = new_name

                    if new_name is None:
                        exc = Exception("Couldn't find new name")
                        if async:
                            task_manager.on_error(task_id, exc)
                        raise exc

                except Exception as e:
                    self._undo_delete_column(base, old_name, column_path, results)
                    if async:
                        task_manager.on_error(task_id, e)
                    # reraise exception to return it as error view
                    raise e

                try:
                    old_base_struct = member.struct
                    member.struct = utils.object2json(dict_base)
                    self.session.flush()

                    # remove base struct from cache
                    model.BASES.bases.pop(member.name)
                    # set new base struct as active
                    self.set_base(member.struct)
                except Exception as e:
                    # undo alter column name
                    try:
                        self._alter_column_name(base, new_name, old_name)
                    except AttributeError:
                        # if current_column is group it doesnt have to undo alter column
                        pass

                    # undo base struct
                    member.struct = old_base_struct
                    self.session.flush()
                    model.BASES.bases.pop(member.name)
                    
                    # undo delete
                    self._undo_delete_column(base, old_name, column_path, results)
                    if async:
                        task_manager.on_error(task_id, e)
                    # reraise exception to be displayed as error msg
                    raise e

                if async:
                    # update task progress
                    # TODO: log result if error
                    task_manager.on_update_progress(
                        task_id, 30.0, msg='Changed relational column name')

                    current_progress = 30.0
                    each_progress = 70.0 / float(len(results)) \
                        if len(results) > 0 else 70.0

                # change all documents
                try:
                    for doc in results:
                        if doc.get(old_name, None):
                            id_doc = doc['_metadata']['id_doc']

                            path = column_path[:-1]
                            if len(path) == 0:
                                path.append(new_name)
                            else:
                                path[-1] = new_name
                            url = '/%s/doc/%d/%s' % (base.metadata.name, id_doc, "/".join(path))
                            params = {
                                'value': doc[old_name],
                                'alter_files': False
                            }
                            request = DummyRequest(path=url, params=params)
                            request.method = 'PUT'
                            request.matchdict = {
                                'base': base.metadata.name,
                                'id': str(id_doc),
                                'path': "/".join(path)
                            }
                            doc_view = DocumentCustomView(DocumentContextFactory(request), request)
                            response = doc_view.put_path()

                            if async:
                                # update task progress
                                current_progress += each_progress
                                # TODO: log result if error
                                task_manager.on_update_progress(
                                    task_id, current_progress,
                                    msg='Setting values on new column')
                except Exception as e:
                    # undo alter column name
                    self._alter_column_name(base, new_name, old_name)

                    # undo base struct
                    member.struct = old_base_struct
                    self.session.flush()
                    model.BASES.bases.pop(member.name)

                    # undo delete
                    self._undo_delete_column(base, old_name, column_path, results)
                    if async:
                        task_manager.on_error(task_id, e)
                    # reraise exception to be displayed as error msg
                    raise e
            else:
                current = current_column.asdict

            if async:
                task_manager.on_success(
                    task_id, update_progress=True,
                    msg='Finished successfully')
                # if async, then close session here
                self.session.commit()
                self.session.close()

            json_current_column = utils.object2json(current)
            return json_current_column
        except Exception as e:
            task_manager.on_error(task_id, e)

        return None

    def _undo_delete_column(self, base, old_name, path, results):
        for doc in results:
            if doc.get(old_name, None):
                id_doc = doc['_metadata']['id_doc']

                url = '/%s/doc/%d/%s' % (base.metadata.name, id_doc, "/".join(path))
                params = {
                    'value': doc[old_name],
                    'alter_files': False
                }
                request = DummyRequest(path=url, params=params)
                request.method = 'PUT'
                request.matchdict = {
                    'base': base.metadata.name,
                    'id': str(id_doc),
                    'path': "/".join(path)
                }
                doc_view = DocumentCustomView(DocumentContextFactory(request), request)
                response = doc_view.put_path()

    def _alter_column_name(self, base, old_name, new_name):
        # create alembic connection and operation object
        db_conn = config.ENGINE.connect()
        alembic_ctx = MigrationContext.configure(db_conn)
        alembic_op = Operations(alembic_ctx)

        doc_table = get_doc_table(
            base.metadata.name,
            config.METADATA,
            **base.relational_fields
        )

        alembic_op.alter_column(
            doc_table.name,
            old_name,
            new_column_name=new_name
        )

        db_conn.close()


    # TODO: validate field data
    def object2content(self, obj, dimension=0, parent_path=[]):
        if obj.get('group'):
            this_path = parent_path[:]
            group_metadata = GroupMetadata(**obj['group']['metadata'])
            this_path.append(group_metadata.name)
            child_path = this_path[:]
            _dimension = dimension
            if group_metadata.multivalued:
                _dimension += 1
            if group_metadata.multivalued:
                child_path.append('*')
            group_content = Content()
            for item in obj['group']['content']:
                content = self.object2content(
                    item,
                    dimension=_dimension,
                    parent_path=parent_path)
                group_content.append(content)
            group = Group(
                metadata=group_metadata,
                content=group_content)
            group.path = this_path
            return group
        elif obj.get('field'):
            field = Field(**obj['field'])
            if field.multivalued:
                field.__dim__ = dimension + 1
            else:
                field.__dim__ = dimension
            this_path = parent_path[:]
            this_path.append(field.name)
            field.path = this_path
            return field
        else:
            raise TypeError('Value must be a Field or Group')

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