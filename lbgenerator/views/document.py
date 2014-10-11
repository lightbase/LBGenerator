
from . import CustomView
from ..lib.validation.document import validate_document_data
from ..lib.validation.document import validate_put_data
from ..lib.validation.path import validate_path_data
from ..lib import utils
from ..lib.log import Logger
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound

class DocumentCustomView(CustomView):

    """ Registry Customized View Methods.
    """
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
        """
        Interprets the path and accesses objects. In detail, the query path
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
        """
        Interprets the path, accesses, and append objects. In detail, the query
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
        index, document = self.get_base().set_path(member.document,
                                self.request.matchdict['path'].split('/'),
                                self.request.params['value']
                                )

        # Build data
        data = validate_put_data(self,
                                dict(value=document),
                                member
                                )

        # Update member
        member = self.context.update_member(member, data)
        return Response(str(index), content_type='application/json')

    def put_path(self, member=None):
        """
        Interprets the path, accesses, and update objects. In detail, the query
        path supported in the current implementation allows the navigation of 
        data according to the tree structure characterizing application objects. 
        The path has the form:

        N1/N2/.../Nn

        where each `N` represents a level(Node) in the tree structure of an 
        object (possibly indicating the collection it belongs to). Specifically,
        every Node represents a collection, or an object identifier, or a field 
        name. 
        """
        # Get raw mapped entity object.
        if member is None:
            member = self.context.get_raw_member(self.request.matchdict['id'])
            if member is None:
                raise HTTPNotFound()

        # Update path
        if self.request.params.get('path') == '/':
            document = member.document

        elif isinstance(self.request.matchdict['path'], list):
            document = self.parse_path_list(member.document)

        else:
            document = self.get_base().put_path(member.document,
                self.request.matchdict['path'].split('/'),
                self.request.params['value'])

        # validate data
        data = validate_put_data(self,
            dict(value=document),
            member)

        if self.request.matchdict['path'] == '_metadata/dt_idx':
            index = False
        else:
            index = True

        # Update member
        member = self.context.update_member(member, data, index=index)
        return Response('UPDATED', content_type='application/json')

    def delete_path(self):
        """
        Interprets the path, accesses, and delete objects keys. In detail, the 
        query path supported in the current implementation allows the navigation
        of data according to the tree structure characterizing application 
        objects. The path has the form:

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

        # Delete path
        document = self.get_base().delete_path(member.document,
            self.request.matchdict['path'].split('/'))

        # Build data
        data = validate_put_data(self,
                                dict(value=document),
                                member
                                )

        # Update member
        member = self.context.update_member(member, data)
        return Response('DELETED', content_type='application/json')

    def full_document(self):
        """ 
        Get files texts and put it into document. Return document with
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
        """ 
        Udpdate database collection of objects. This method needs a valid JSON
        query, a valid query path and the object to update. Will query database
        objects, and update each path to the new object. Return count of
        successes and failures.
        """
        collection = self.get_collection(render_to_response=False)
        success, failure = 0, 0
        path = self.request.params['path']

        if path[0] == '[':
            path = utils.json2object(path)
        self.request.matchdict['path'] = path

        for member in collection:
            # Override matchdict
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
        """ 
        Delete database collection of objects. This method needs a valid JSON
        query and a valid query path . Will query database objects, and update 
        each path (deleting the respective path). Return count of successes and 
        failures.
        """
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

    def parse_path_list(self, document):

        operations = self.request.matchdict['path']
        for operation in operations:
            if 'delete' in operation:
                operatefn = self.path_delete_op
            elif 'insert' in operation:
                operatefn = self.path_insert_op
            else:
                operatefn = self.path_update_op
            document = operatefn(document, operation)
        return document

    def path_update_op(self, document, operation):
        """
        case zero: change value of path.
        example:
        [{    
            "path": "field",   
            "value": "875.637.971-49"
        },{    
            "path": "group/*/field",   
            "value": "y" 
        }]

        first case: change only if equals.
        example:
        [{    
            "path": "field",   
            "equals": "877.756757",
            "value": "875.637.971-49"
        },{    
            "path": "group/*/field",   
            "equals": "x", 
            "value": "y" 
        }]
        """

        class UpdatePath(object):

            def __init__(self, path, value, **ops):
                if ops:
                    self.op_name = list(ops.keys())[0]
                    self.op_value = list(ops.values())[0]
                    callfn = getattr(self, '_' + self.op_name)
                    self._callfn = callfn
                else:
                    self._callfn = lambda arg: True

            def __call__(self, *args, **kw):
                return self._callfn(*args, **kw)

            def _equals(self, value):
                if value == self.op_value:
                    return True
                return False

        updatefn = UpdatePath(**operation)
        document = self.get_base().put_path(
            document,
            operation['path'].split('/'),
            operation['value'],
            fn=updatefn)

        return document

    def path_insert_op(self, document, operation):
        """
        second case: add repetition to multivalued structure.
        example:
        [{    
            "path": "group",   
            "insert": {
                "field1": "value",
                "field2": "value"
            }
        },{    
            "path": "field",   
            "insert": "value"
        }]
        """
        zero, document = self.get_base().set_path(
            document,
            operation['path'].split('/'),
            operation['insert'])
        return document

    def path_delete_op(self, document, operation):
        """

        third case: delete repetition (if equals) from multivalued structure.
        example:
        [{    
            "path": "field",   
            "delete": "value"
        }]
        """
        document = self.get_base().delete_path(
            document,
            operation['path'].split('/'))
        return document
