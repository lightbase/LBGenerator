"""
This file contains the basic LBOperation class and other 
CRUD operations for the Lightbase API

Creator: Danilo Carvalho
"""

import logging

from liblightbase.lbutils.codecs import json2object
from liblightbase.lbutils.codecs import object2json
from liblightbase.lbutils.conv import dict2base
from liblightbase.lbutils.conv import dict2document
from liblightbase.lbutils.conv import document2dict
from liblightbase.lbtypes import Matrix

# temp
LBG_URL_API = "http://192.168.56.102/lbg"

class LBOperation(object):
    """
    Basic operation class. All operations must inherit from this class.

    Creator: Danilo Carvalho
    """
    default_error_msg = "Operation not implemented"

    def __init__(self, params, transaction=False):
        self.logger = logging.getLogger("DEBUG")
        self.params = params
        self.transaction = transaction

    # TODO: define arguments and return value
    def _on_pre_execute(self):
        """ 
        Work that all operations must do _before_ execution. 
        Ex: check authentication and authorization.

        This method is optional, but all operations that implement it
        must call "super()._on_pre_execute()".
        """
        pass

    # TODO: define arguments and return value
    def _on_execute(self):
        """ 
        The operation itself. 
        All operations must implement this method.
        """
        raise NotImplementedError("Operation's _on_execute() method is not implemented")

    # TODO: define arguments and return value
    def _on_post_execute(self):
        """ 
        Work that all operations must do _after_ execution.
        Ex: log operation.

        This method is optional, but all operations that implement it
        must call "super()._on_pre_execute()".
        """

        # if it's not a transaction, close session immediately
        if not self.transaction:
            context = self.get_context()
            if context is not None:
                context.session.commit()
                context.session.close()

    # TODO: define arguments and return value
    def run(self):
        """ 
        Run the operation.
        Returns a dictionary with results (dictionary keys to be defined)
        """
        self._on_pre_execute()
        result = self._on_execute()
        self._on_post_execute()

        return result

    def get_context(self):
        """
        TODO:
        Gets the current session context.
        """
        if not hasattr(self, "context"):
            return None

        return self.context

# ---=== Base CRUD ===--- #

class BaseOperation(LBOperation):
    """
    Base operation for manipulating Bases in Lightbase.
    All operations involving Bases should inherit from this class.

    Creator: Danilo Carvalho
    """
    def _on_pre_execute(self):
        super()._on_pre_execute()

    def _get_context(self, method="POST", basename=None):
        from ..model.context.base import BaseContextFactory
        from pyramid.testing import DummyRequest

        if basename is not None:
            dummy_path = "/%s" % (basename)
        else:
            dummy_path = "/"

        dummy_request = DummyRequest(path=dummy_path)
        dummy_request.method = method

        if basename is not None:
            dummy_request.matchdict = { "base": basename }    

        context = BaseContextFactory(dummy_request)

        return context

    def validate_base_data(self, base_data, task='CREATE', basename=None):
        valid_fields = (
            'metadata',
            'content',
            )

        from ..lib import utils
        data = utils.filter_params(base_data, valid_fields)

        for field in valid_fields:
            if field not in data:
                raise Exception('Required field: %s' % (field))

        json_base = utils.json2object(data)

        if task == 'CREATE':
            json_base['metadata']['id_base'] = self.context.get_next_id()
            import datetime
            json_base['metadata']['dt_base'] = datetime.datetime.now()

            base = dict2base(json_base)

            # Estrutura na tabela.
            data = dict(
                id_base = base.metadata.id_base,
                dt_base = base.metadata.dt_base,
                name = base.metadata.name,
                struct = base.asdict,
                idx_exp = base.metadata.idx_exp,
                idx_exp_url = base.metadata.idx_exp_url,
                idx_exp_time= base.metadata.idx_exp_time,
                file_ext = base.metadata.file_ext,
                file_ext_time = base.metadata.file_ext_time,
                txt_mapping = base.metadata.txt_mapping
            )

        elif task == 'UPDATE':
            if basename is None:
                basename = self.params['basename']

            member = self.context.get_member(basename)

            json_base['metadata']['id_base'] = member.id_base
            json_base['metadata']['dt_base'] = member.dt_base
            base = self.context.set_base(json_base)

            data = dict(
                name = base.metadata.name,
                struct = base.json,
                idx_exp = base.metadata.idx_exp,
                idx_exp_url = base.metadata.idx_exp_url,
                idx_exp_time= base.metadata.idx_exp_time,
                file_ext = base.metadata.file_ext,
                file_ext_time = base.metadata.file_ext_time,
                txt_mapping = base.txt_mapping_json
            )

        return data

class CreateBaseOperation(BaseOperation):
    """
    Creates a new base in the Lightbase database

    Params:
     - data (dict): model of the base with fields "metadata" and "content"

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao criar base!"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        self.logger.debug("CreateBaseOperation._on_pre_execute()")
        # validate base data
        self.context = self._get_context(method="POST")
        self.validated_base_data = self.validate_base_data(self.params['data'])


    def _on_execute(self):
        self.logger.debug("CreateBaseOperation._on_execute()")
        try:
            self.context.create_member(self.validated_base_data)
        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao criar base!',
                'systemObject': str(e)
            }

        # TODO: what else to return?
        return { "success": True }


    def _on_post_execute(self):
        super()._on_post_execute()
        self.logger.debug("CreateBaseOperation._on_post_execute()")


class ReadBaseOperation(BaseOperation):
    """
    Reads the base's metadata

    Params:
     - basename (string): name of the base

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao ler base!"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        self.context = self._get_context(method="GET", 
            basename=self.params["basename"])

    def _on_execute(self):
        try:
            basename = self.params["basename"]
            base = self.context.get_member(basename)
            if base is None:
                # TODO: error
                raise RuntimeError("Base não encontrada.")
            base_json = base.struct
            base_dict = json2object(base_json)
        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao ler base!',
                'systemObject': str(e)
            }

        return {
            "success": True,
            "data": base_dict
        }


class DeleteBaseOperation(BaseOperation):
    """
    Deletes a base (and all it's documents and files) from the database
    Warning: This operation has no undo operaton yet, so be careful!!!

    Params:
     - basename (string): name of the base

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao apagar base!"

    def _on_pre_execute(self):
        super()._on_pre_execute()

        basename = self.params['basename']
        self.context = self._get_context(method="DELETE", 
            basename=basename)

    def _on_execute(self):
        try:
            basename = self.params["basename"]

            base = self.context.delete_member(basename)
            if base is None:
                raise RuntimeError("Base não encontrada.")

            # TODO: clear cache??
        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao apagar base!',
                'systemObject': str(e)
            }

        return { "success": True }


# ---=== Document CRUD ===--- #

class DocumentOperation(LBOperation):
    """
    Base operation for manipulating Documents in Lightbase.
    All operations involving Documents should inherit from this class.

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao acessar registro"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        # try:
        #     # get Base obj
        #     base_name = self.params["basename"]
        #     base_rest = BaseREST(LBG_URL_API)
        #     self.base = base_rest.get(base_name)
        # except Exception as e:
        #     raise RuntimeError("Base não encontrada: " + base_name)

    def _get_context(self, method="POST"):
        from ..model.context.document import DocumentContextFactory
        from pyramid.testing import DummyRequest

        dummy_path = "/%s/doc" % (self.params['basename'])
        dummy_request = DummyRequest(path=dummy_path)
        dummy_request.method = method
        dummy_request.matchdict = { "base": self.params['basename'] }
        context = DocumentContextFactory(dummy_request)

        return context


    def _validate_doc_data(self, data, doc=None):
        if 'validate' in self.params and self.params['validate'] == '0':
            validate = False
        else:
            validate = True

        # Get Base object
        # from .. import model
        base = self.context.get_base()

        # Parse JSON object
        from ..lib import utils
        document = utils.json2object(data)

        from liblightbase.lbdoc.metadata import DocumentMetadata
        import datetime

        if doc is not None:
            dt_idx = document.get('_metadata', { }).get('dt_idx', None)

            if dt_idx and not isinstance(dt_idx, datetime.datetime):
                dt_idx = datetime.datetime.strptime(dt_idx, '%d/%m/%Y %H:%M:%S')

            # Build Metadata
            _metadata = DocumentMetadata(**dict(
                id_doc = doc.id_doc,
                dt_doc = doc.dt_doc,
                dt_last_up = datetime.datetime.now(),
                dt_idx = dt_idx,
                dt_del = doc.dt_del
            ))
        else:
            # SELECT next id from sequence
            doc_id = self.context.entity.next_id()

            # Build Metadata
            now = datetime.datetime.now()
            _metadata = DocumentMetadata(doc_id, now, now)

        (document, # Document it self.
        reldata, # Relational data.
        files, # All existent files within document.
        cfiles # All non-existent (will be created) files within document.
        ) = base.validate(document, _metadata, validate)

        # Normalize relational data
        [self._fix_matrix(reldata[field]) for field in reldata if isinstance(reldata[field], Matrix)]

        data = {}

        # Build database object
        data['document'] = document
        data['__files__'] = files
        data.update(_metadata.__dict__)
        data.update(reldata)

        return data


    def _fix_matrix(self, mat):
        inner_lens = [len(mat[i]) for i, v in enumerate(mat) if isinstance(mat[i], Matrix)]
        for i, v in enumerate(mat):
            if type(mat[i]) is type(None) and len(inner_lens) > 0:
                mat[i] = [None] * max(inner_lens)
            elif isinstance(mat[i], Matrix):
                if len(mat[i]) < max(inner_lens):
                    [mat[i].append(None) for _ in range(max(inner_lens)-len(mat[i]))]
                fix_matrix(mat[i])

class CreateDocumentOperation(DocumentOperation):
    """
    Creates a new document in a base.

    Params:
     - basename (string): name of the base
     - data (dict): contents of the new document

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao criar registro"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        # get context
        self.context = self._get_context(method="POST")
        # validate document data
        self.validated_doc_data = self._validate_doc_data(self.params['data'])

    def _on_execute(self):
        # TODO
        self.logger.debug("CreateDocumentOperation._on_execute()")

        try:
            doc = self.context.create_member(self.validated_doc_data)
            self.doc_id = int(self.context.get_member_id(doc))
        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao inserir registro!',
                'systemObject': str(e)
            }

        # TODO: what else to return?
        return {
            "success": True,
            "doc_id": self.doc_id
        }
            

class ReadDocumentOperation(DocumentOperation):
    """
    Reads the contents of a document

    Params:
     - basename (string): name of the base
     - doc_id (int): id of the document to be read

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao ler registro"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        # get context
        self.context = self._get_context(method="GET")

    def _on_execute(self):
        self.logger.debug("ReadDocumentOperation._on_execute()")

        try:
            doc_id = self.params["doc_id"]

            doc = self.context.get_member(doc_id)
            if doc is None:
                raise RuntimeError("Registro não encontrado.")

            doc_dict = doc.document
        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao recuperar registro!',
                'systemObject': str(e)
            }

        return { 
            "success": True,
            "data": doc_dict
        }

class ReadFullDocumentOperation(DocumentOperation):
    """
    Reads the contents of a document, including the contents indexed in 
    its files

    Params:
     - basename (string): name of the base
     - doc_id (int): id of the document to be read

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao ler registro completo"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        # get context
        self.context = self._get_context(method="GET")

    def _on_execute(self):
        self.logger.debug("ReadFullDocumentOperation._on_execute()")

        try:
            doc_id = self.params["doc_id"]

            # Get raw mapped entity object.
            member = self.context.get_raw_member(doc_id)
            if member is None:
                # TODO: error
                raise RuntimeError('Registro não encontrado')

            doc_dict = self.context.get_full_document(json2object(member.document))
        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao recuperar registro!',
                'systemObject': str(e)
            }

        return { 
            "success": True,
            "data": doc_dict
        }

class PartialReadDocumentOperation(DocumentOperation):
    """

    """
    default_error_msg = "Erro ao ler parte de registro"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        # get context
        self.context = self._get_context(method="GET")

    def _on_execute(self):
        self.logger.debug("PartialReadDocumentOperation._on_execute()")

        try:
            doc_id = self.params["doc_id"]
            path = self.params["path"]

            # Get raw mapped entity object.
            member = self.context.get_raw_member(doc_id)
            if member is None:
                # TODO: error
                raise RuntimeError('Registro não encontrado')

            doc_dict = self.context.get_base().get_path(
                member.document,
                path.split("/")
            )
        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao recuperar registro!',
                'systemObject': str(e)
            }

        return { 
            "success": True,
            "data": doc_dict
        }

class ListDocumentOperation(DocumentOperation):
    """
    Lists or searches documents in a base

    Params:
     - basename (string): name of the base
     - search_params (dict) [optional]: a dictionary / json object containing 
        search parameters. Check http://mediawiki.brlight.net/index.php/Select 
        for details.

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao listar registros"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        # get context
        self.context = self._get_context(method="GET")

    def _on_execute(self):
        self.logger.debug("ListDocumentOperation._on_execute()")
        try:
            # TODO: search params
            search_params = self.params.get('search_params', '{}')
            query = json2object(search_params)

            doc_collection = self.context.get_collection(query)
            docs = list()

            for doc_tuple in doc_collection:
                # tuple = (??, doc_id, doc_data, update_at?, ??)
                doc = doc_tuple[2]
                docs.append(doc)

        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao atualizar registro!',
                'systemObject': str(e)
            }

        return {
            "success": True,
            "data": docs
        }

class UpdateDocumentOperation(DocumentOperation):
    """
    Updates a document.
    
    Warning: this is a full update! All fields and groups not included in the
    parameters will be deleted! This includes multivalued fields/groups.
    For a partial update, see the PartialUpdateDocumentOperation class.

    Params:
     - basename (string): name of the base
     - doc_id (int): id of the document to be updated
     - data (dict): all contents of the document

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao atualizar registro"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        # get context
        self.context = self._get_context(method="PUT")

    def _on_execute(self):
        self.logger.debug("UpdateDocumentOperation._on_execute()")

        try:
            doc_id = self.params["doc_id"]
            data = self.params["data"]

            doc = self.context.get_member(doc_id, close_sess=False)
            if doc is None:
                # TODO:
                raise RuntimeError("Registro não encontrado")

            # validate document data
            self.validated_doc_data = self._validate_doc_data(data, doc=doc)

            self.context.update_member(doc, self.validated_doc_data)
        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao atualizar registro!',
                'systemObject': str(e)
            }

        # TODO: what else to return?
        return { "success": True }


class PartialUpdateDocumentOperation(UpdateDocumentOperation):
    """
    Updates parts of a document.
    This operation will only alter the fields that are present in the
    parameters. Other fields will be left unchanged. Multivalued fields 
    or groups can also be partially altered using this operation (see 
    Param "data" below for more information).

    Params:
     - basename (string): name of the base
     - doc_id (int): id of the document to be updated
     - data (dict): altered contents of the document.
        For multivalued fields, its value can be either the full array of values 
        or an array of commands.
        
        If an array of values is given, the field will be fully replaced by the
        provided array. For example:
        
            "data": { "multivalued_field": ["value1", "value2"] }
        
        This will replace everything in the document's "multivalued_field" with 
        the values ["value1", "value2"]
        
        If you need to change only a few elements inside "multivalued_field" you can
        send an array of commands. Each command is a JSON object (or dictionary) in
        the form:
        
            { "$command": value }

        Where 'value' is of whatever type the actual field expects: string,
        array, object, boolean, etc..
        
        Available commands:
            { "$set#[pos]" : value } -> edit value in position [pos]
            { "$add" : value } -> add value at the end of list
            { "$add#[pos]" : "value" } -> add value in position [pos] and push 
                back the rest
            { "$remove": null } -> remove the last value from the list
            { "$remove#[pos]" : null } -> remove value in position [pos] and pull 
                back the rest
            { "$multi#[pos-start]#[pos-end]" : 
                [ "value-pos-start", ..., "value-pos-end" ] -> change all values 
                    from position [pos-start] to position [pos-end] (inclusive)
        Example:
            "data": { "multivalued_field": [
                { "$set#0": "value1" },
                { "$remove": null }
            ]}

        The example will change the first value to "value1" and delete the last 
        value in the field.

    Creator: Danilo Carvalho
    """
    def _on_pre_execute(self):
        super()._on_pre_execute()
        # get context
        self.context = self._get_context(method="PUT")

    def _on_execute(self):
        self.logger.debug("PartialUpdateDocumentOperation._on_execute()")

        try:
            doc_id = self.params["doc_id"]
            update_doc_dict = self.params["data"]

            doc = self.context.get_member(doc_id, close_sess=False)    
            if doc is None:
                # TODO:
                raise RuntimeError("Registro não encontrado")

            self._update_dict(doc.document, update_doc_dict)

            # validate document data
            self.validated_doc_data = self._validate_doc_data(doc.document, doc=doc)

            self.context.update_member(doc, self.validated_doc_data)
        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao atualizar registro!',
                'systemObject': str(e)
            }

        # TODO: what else to return?
        return { "success": True }

    def _update_dict(self, doc_dict, update_doc_dict):
        """
        Updates the document's data (doc_dict) with data from update_doc_dict.
        Keys and subkeys that aren't present in updated_doc_dict are left unchanged.
        Args:
         - doc_dict: the full document to be updated
         - update_doc_dict: a dict with only the keys that will be changed
        """
        for key, value in update_doc_dict.items():
            if isinstance(value, dict) and key in doc_dict:
                self._update_dict(doc_dict[key], update_doc_dict[key])
            elif isinstance(value, list) and key in doc_dict and self._is_list_descriptor(value):
                self._update_list(doc_dict[key], update_doc_dict[key])
            else:
                doc_dict[key] = value

    def _is_list_descriptor(self, the_list):        
        first_item = the_list[0] if len(the_list) > 0 else None

        if isinstance(first_item, dict):
            for key in first_item:
                if key.startswith("$"):
                    return True

        return False

    def _update_list(self, doc_list, update_doc_list):
        # check if items are update descriptors:
        # { "$set#[pos]" : "value" } -> edit value in position [pos]
        # { "$add" : "value" } -> add value at the end of list
        # { "$add#[pos]" : "value" } -> add value in position [pos] and push back the rest
        # { "$remove": null } -> remove last value form list
        # { "$remove#[pos]" : null } -> remove value in position [pos] and pull back the rest
        # { "$multi#[pos-start]#[pos-end]" : [ "value-pos-start", ..., "value-pos-end" ] -> change all values 
        #               from position [pos-start] to position [pos-end] (inclusive)

        for descriptor in update_doc_list:
            for key, value in descriptor.items():
                args = key.split("#")
                command = args[0]
                args = args[1:]

                command_func = PartialUpdateDocumentOperation.valid_descriptors.get(command, None)
                if command_func is None:
                    # TODO: ERROR invalid command
                    pass

                command_func(self, doc_list, value, *args)


    def _list_set(self, doc_list, value, *args):
        # TODO: check args size, check if its int
        pos = int(args[0])
        if (len(doc_list) > pos):
            if isinstance(value, dict):
                self._update_dict(doc_list[pos], value)
            elif isinstance(value, list) and self._is_list_descriptor(value):
                # TODO: arrays
                self._update_list(doc_list[pos], value)
            else:
                doc_list[pos] = value
        else:
            # TODO: ERROR position doesn't exist
            pass

    def _list_add(self, doc_list, value, *args):
        if len(args) > 0:
            # TODO: check if its int
            pos = int(args[0])
            doc_list.insert(pos, value)
        else:
            # append to the end of list
            doc_list.append(value)

    def _list_remove(self, doc_list, value, *args):
        if len(args) > 0:
            # TODO: check if its int
            pos = int(args[0])
            del doc_list[pos]
        else:
            # remove last
            doc_list.pop()

    def _list_multi(self, doc_list, value, *args):
        if len(args) > 1 and isinstance(value, list):
            pos_start = int(args[0])
            pos_end = int(args[1])
                        
            num_elements = pos_end - pos_start + 1
            if num_elements != len(value):
                # TODO ERROR
                pass

            current_pos = pos_start

            for i in range(0, num_elements):
                if (len(doc_list) > current_pos):
                    if isinstance(value[i], dict):
                        self._update_dict(doc_list[current_pos], value[i])
                    elif isinstance(value[i], list) and self._is_list_descriptor(value[i]):
                        self._update_list(doc_list[current_pos], value[i])
                    else:
                        doc_list[current_pos] = value[i]
                else:
                    # TODO: add to end or fail?
                    # adding to the end
                    doc_list.append(value[i])

                current_pos += 1
        else:
            # TODO: ERROR
            pass

    valid_descriptors = { 
        "$set" : _list_set, 
        "$add" : _list_add, 
        "$remove" : _list_remove, 
        "$multi" : _list_multi
    }

            
class DeleteDocumentOperation(DocumentOperation):
    """
    Deletes a document from a base.

    Params:
     - basename (string): name of the base
     - doc_id (int): id of the document to be deleted

    Creator: Danilo Carvalho
    """

    default_error_msg = "Erro ao apagar registro"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        # get context
        self.context = self._get_context(method="DELETE")

    def _on_execute(self):
        self.logger.debug("DeleteDocumentOperation._on_execute()")

        try:
            doc_id = self.params["doc_id"]

            is_deleted = self.context.delete_member(doc_id)
            # Check if the number of deleted rows is different than 0
            if is_deleted.__dict__['rowcount'] == 0:
                # TODO:
                raise RuntimeError("Registro não encontrado")
        except Exception as e:
            return {
                'success': False, 
                'error_message': 'Erro ao apagar registro!',
                'systemObject': str(e)
            }

        return { "success": True }


# ---=== File CRUD ===--- #

class FileOperation(DocumentOperation):
    """
    Base operation for manipulating Files in Lightbase.
    All operations involving Files should inherit from this class.

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro em operação com arquivo"

    def validate_file_data(self, data):
        import uuid
        import base64

        if "filename" not in data:
            raise RuntimeError("Campo 'filename' não encontrado.")

        if "base64" not in data:
            raise RuntimeError("Compo 'base64' não encontrado.")

        if "file_size" not in data:
            raise RuntimeError("Compo 'file_size' não encontrado.")

        # TODO: other missing fields?

        filemask = {
           'uuid': str(uuid.uuid4()),
           'filename': data["filename"],
           'filesize': data["file_size"],
           'mimetype': data["mimetype"] if "mimetype" in data else "application/octet-stream",
        }

        namespace = uuid.UUID(filemask['uuid'])
        name = str(hash(frozenset(filemask.items())))
        id_file = str(uuid.uuid3(namespace, name))
        filemask['id_file'] = id_file

        file_data = base64.standard_b64decode(bytes(data['base64'], 'utf-8'))

        data = {
           'id_doc': None,
           'file': file_data,
           'filetext': None,
           'dt_ext_text': None
        }

        data.update(filemask)
        data.pop('uuid')

        return data, filemask

    def _get_context(self, method="POST"):
        from ..model.context.file import FileContextFactory
        from pyramid.testing import DummyRequest

        dummy_path = "/%s/file/" % (self.params['basename'])
        dummy_request = DummyRequest(path=dummy_path)
        dummy_request.method = method
        dummy_request.matchdict = { "base": self.params['basename'] }
        context = FileContextFactory(dummy_request)

        return context


class MultipartCreateFileOperation(FileOperation):
    """
    Uploads a new file to the base via a multipart/form-data request

    Params:
     - basename (string): name of the base
     - data (cgi.FieldStorage): the file as a FieldStorage

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao criar arquivo"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        self.context = self._get_context(method="POST")


    def _on_execute(self):
        self.logger.debug("MultipartCreateFileOperation._on_execute()")

        try:
            data, self.filemask = self.validate_file_data(self.params['data'])
            member = self.context.create_member(data)
        except Exception as e:
            return {
                'success': False,
                'error_message': CreateFileOperation.default_error_msg,
                'systemObject': str(e)
            }

        return {
            "success": True,
            "data": self.filemask
        }

    def validate_file_data(self, file_data):
        import uuid
        import base64

        filemask = {
           'uuid': str(uuid.uuid4()),
           'filename': file_data.filename,
           'filesize': self._get_file_size(file_data.file),
           'mimetype': file_data.type,
        }

        namespace = uuid.UUID(filemask['uuid'])
        name = str(hash(frozenset(filemask.items())))
        id_file = str(uuid.uuid3(namespace, name))
        filemask['id_file'] = id_file

        data = {
           'id_doc': None,
           'file': file_data.file.read(),
           'filetext': None,
           'dt_ext_text': None
        }

        data.update(filemask)
        data.pop('uuid')
        return data, filemask

    def _get_file_size(self, file_stream):
        file_stream.seek(0, 2)
        size = file_stream.tell()
        # move the cursor to the begin of the file
        file_stream.seek(0)
        return size


class CreateFileOperation(FileOperation):
    """
    Uploads a new file to the base.
    This operations receives the file as a base64 encoded string.

    Params:
     - basename (string): name of the base
     - filename (string): name of the file being uploaded
     - file_size (int): size of the file in bytes
     - mimetype (string) [optional]: mimetype of the file (ex: "image/jpg")
     - base64 (string): the file data as a base64 encoded string

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao criar arquivo"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        self.context = self._get_context(method="POST")

    def _on_execute(self):
        self.logger.debug("CreateFileOperation._on_execute()")

        try:            
            data, self.filemask = self.validate_file_data(self.params['data'])
            member = self.context.create_member(data)
        except Exception as e:
            return {
                'success': False, 
                'error_message': CreateFileOperation.default_error_msg,
                'systemObject': str(e)
            }

        return {
            "success": True,
            "data": self.filemask
        }


class ReadFileOperation(FileOperation):
    """
    Reads the metadata of a file in Lightbase.

    Params:
     - basename (string): name of the base
     - file_id (int): id of the file to be read

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao ler arquivo"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        self.context = self._get_context(method="GET")

    def _on_execute(self):
        self.logger.debug("ReadFileOperation._on_execute()")

        try:
            file_id = self.params["file_id"]
            members = self.context.get_member(file_id)
            if members is None:
                raise RuntimeError("Arquivo não encontrado")
            files = []
            for member in members:
                files.append(self.member_to_dict(member))
        except Exception as e:
            return {
                'success': False,
                'error_message': ReadFileOperation.default_error_msg,
                'systemObject': str(e)
            }

        return {
            "success": True,
            "data": files
        }

    def member_to_dict(self, member):
        if len(member) < 7:
            raise RuntimeError(ReadFileOperation.default_error_msg)
        file_id = member[0]
        domain_url = self.params['request_url'].strip('/lbrad')
        download_url = "%s/%s/file/%s/download" % \
            (domain_url, self.params['basename'], file_id)

        return {
            "file_id": file_id,
            "doc_id": member[1],
            "filename": member[2],
            "mimetype": member[3],
            "file_size": member[4],
            "filetext" : member[5],
            "dt_ext_text": member[6],
            "download": download_url,
        }


class DeleteFileOperation(FileOperation):
    """
    Deletes a file from Lightbase.

    Params:
     - basename (string): name of the base
     - file_id (string): id of the file to be deleted

    Creator: Danilo Carvalho
    """
    default_error_msg = "Erro ao apagar arquivo"

    def _on_pre_execute(self):
        super()._on_pre_execute()
        self.context = self._get_context(method="DELETE")

    def _on_execute(self):
        self.logger.debug("DeleteFileOperation._on_execute()")

        try:
            file_id = self.params["file_id"]

            success = self.context.delete_member(file_id)
            if not success:
                raise RuntimeError("Arquivo não deletado")
        except Exception as e:
            return {
                'success': False,
                'error_message': DeleteFileOperation.default_error_msg,
                'systemObject': str(e)
            }

        return {
            'success': True
        }
