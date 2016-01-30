from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound

from . import CustomView
from ..lib.validation.document import validate_document_data
from ..lib.validation.document import validate_put_data
from ..lib.validation.path import validate_path_data
from ..lib import utils
from ..lib.log import Logger
from ..lib.path import parse_list_pattern

from ..perf_profile import pprofile


class DocumentCustomView(CustomView):
    """ Registry Customized View Methods."""

    def __init__(self, context, request):
        super(DocumentCustomView, self).__init__(context, request)
        self.logger = Logger(__name__)

    def _get_data(self, *args):
        """ Get all valid data from (request) POST or PUT.
        """
        return validate_document_data(self, self.request, *args)

    def get_member(self):
        id = self.request.matchdict['id']
        self.wrap = False
        member = self.context.get_member(id)
        return self.render_to_response(member)

    def get_path(self):
        """Interprets the path and accesses objects. In detail, the query path
        supported in the current implementation allows the navigation of data 
        according to the tree structure characterizing application objects. 
        The path has the form:

        N1/N2/.../Nn

        where each `N` represents a level(Node) in the tree structure of an 
        object (possibly indicating the collection it belongs to). Specifically,
        every Node represents a collection, or an object identifier, or a field 
        name.
        """

        # Get raw mapped entity object.
        member = self.context.get_raw_member(self.request.matchdict['id'])
        if member is None:
            raise HTTPNotFound()

        # Access inner object.
        document = self.get_base().get_path(member.document,
            self.request.matchdict['path'].split('/'))

        response = utils.object2json(document)
        return Response(response, content_type='application/json')

    def set_path(self):
        """Interprets the path, accesses, and append objects. In detail, the query
        path supported in the current implementation allows the navigation of 
        data according to the tree structure characterizing application objects. 
        The path has the form:

        N1/N2/.../Nn

        where each `N` represents a level(Node) in the tree structure of an 
        object (possibly indicating the collection it belongs to). Specifically,
        every Node represents a collection, or an object identifier, or a field 
        name. The last Node (Nn) must return a list object, so we can append 
        the new object to it.
        """

        # Get raw mapped entity object.
        member = self.context.get_raw_member(self.request.matchdict['id'])
        if member is None:
            raise HTTPNotFound()

        # Set path
        list_pattern = [{
            'path': self.request.matchdict['path'],
            'mode':'insert',
            'args': [self.request.params['value']]
        }]
        document = parse_list_pattern(
            self.get_base(),
            member.document,
            list_pattern)

        # Build data
        data = validate_put_data(self,
            dict(value=document),
            member)

        # Update member
        member = self.context.update_member(member, data)
        return Response('OK', content_type='application/json')

    def put_path(self, member=None):
        """Interprets the path, accesses, and update objects. In detail, 
        the query path supported in the current implementation allows 
        the navigation of data according to the tree structure 
        characterizing application objects. The path has the form:

        N1/N2/.../Nn

        where each `N` represents a level(Node) in the tree structure 
        of an object (possibly indicating the collection it belongs 
        to). Specifically, every Node represents a collection, or an 
        object identifier, or a field name. 
        """

        # NOTE: Get raw mapped entity object!
        if member is None:
            member = self.context.get_raw_member(self.request.matchdict['id'])
            if member is None:
                raise HTTPNotFound()

        # NOTE: Update path!
        if self.request.params.get('path') == '/':
            document = member.document
        elif isinstance(self.request.matchdict['path'], list):
            document = parse_list_pattern(
                self.get_base(), 
                member.document, 
                self.request.matchdict['path'])
        else:
            list_pattern = [{
                'path': self.request.matchdict['path'],
                'mode':'update',
                'args': [self.request.params['value']]
            }]
            document = parse_list_pattern(
                self.get_base(), 
                member.document, 
                list_pattern)

        # NOTE: Validate data!
        data = validate_put_data(
            self, 
            dict(value=document), 
            member)

        esp_cmd = None
        try:
            esp_cmd = self.request.params["esp_cmd"]
        except Exception as e:
            pass

        # NOTE: Como o parâmetro "esp_cmd" é opcional ele não está 
        # declarado na rota e não entra em "self.request.matchdict"! 
        # By Questor
        if esp_cmd == "dont_idx":
            index = False
        else:
            index = True

        # NOTE: Update member!
        member = self.context.update_member(member, data, index=index)

        return Response('UPDATED', content_type='application/json')

    def delete_path(self):
        """Interprets the path, accesses, and delete objects keys. In detail, the 
        query path supported in the current implementation allows the navigation
        of data according to the tree structure characterizing application 
        objects. The path has the form:

        N1/N2/.../Nn

        where each `N` represents a level(Node) in the tree structure of an 
        object (possibly indicating the collection it belongs to). Specifically,
        every Node represents a collection, or an object identifier, or a field 
        name. 
        """

        # Obtêm o registro do banco de dados
        member = self.context.get_raw_member(self.request.matchdict['id'])
        if member is None:
            raise HTTPNotFound()

        # Aqui define o caminho e a operação dentro de tuplas em um 
        # array.
        list_pattern = [{
            'path': self.request.matchdict['path'],
            'mode':'delete'}]

        # Define a operação x caminho e as funções executantes da tarefa via
        # delegate.
        document = parse_list_pattern(
            self.get_base(),
            member.document,
            list_pattern)

        # Build data
        data = validate_put_data(self,
            dict(value=document),
            member)

        # Update member
        member = self.context.update_member(member, data)
        return Response('TESTE', content_type='application/json')

    def full_document(self):
        """Get files texts and put it into document. Return document with
        files texts.
        """

        # Get raw mapped entity object.
        member = self.context.get_raw_member(self.request.matchdict['id'])

        if member is None:
            raise HTTPNotFound()

        document = self.context.get_full_document(utils.json2object(member.document))

        return Response(utils.object2json(document),
                       content_type='application/json')

    def update_collection(self):
        """Udpdate database collection of objects. This method needs a 
        valid JSON query, a valid query path and the object to update. 
        Will query database objects, and update each path to the new 
        object. Return count of successes and failures.
        """

        self.context.result_count = False
        collection = self.get_collection(render_to_response=False)
        success, failure = 0, 0
        path = self.request.params['path']

        if path[0] == '[':
            path = utils.json2object(path)

        self.request.matchdict['path'] = path

        for member in collection:

            # NOTE: Override matchdict!
            self.request.matchdict['id'] = member.id_doc

            if not self.context.session.is_active:
                self.context.session.begin()

            try:
                self.put_path(member)
                success = success + 1
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                failure = failure + 1
            finally:
                if self.context.session.is_active:
                    self.context.session.close()

        return Response('{"success": %d, "failure" : %d}'
                        % (success, failure),
                        content_type='application/json')

    def delete_collection(self):
        """Delete database collection of objects. This method needs a valid JSON
        query and a valid query path . Will query database objects, and update 
        each path (deleting the respective path). Return count of successes and 
        failures.
        """
        self.context.result_count = False
        collection = self.get_collection(render_to_response=False)
        success, failure = 0, 0

        for member in collection:
            # Override matchdict
            self.request.matchdict = {'path': self.request.params.get('path'),
                                      'id': member.id_doc}

            if not self.context.session.is_active:
                self.context.session.begin()
            try:
                if self.request.matchdict['path'] is None:
                    self.context.delete_member(member.id_doc)
                else:
                    self.delete_path()
                success = success + 1

            except Exception as e:
                failure = failure + 1

            finally:
                if self.context.session.is_active:
                    self.context.session.close()

        return Response('{"success": %d, "failure" : %d}'
                        % (success, failure),
                        content_type='application/json')
