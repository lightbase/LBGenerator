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
            document = parse_list_pattern(self.get_base(),
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








    # def full_documents(self):
    #     """ Get files texts and put it into document. Return document 
    #     with files texts.
    #     """

    #     # Get raw mapped entity object.
    #     list_id_doc = [4896904, 2509363, 3200355, 1780891, 2615735, 2551419, 1850880, 2548582, 3033881, 3633578, 2398488, 3313261, 1604495, 1606127, 1612709, 1633895, 1622679, 1625739, 1633245, 1604485, 2634350, 1620042, 2480168, 2518671, 2522378, 2548803, 1803758, 3040116, 4897541, 3049936, 1633928, 1636348, 2567345, 1848958, 1634377, 2510261, 1628303, 1628053, 1628666, 1620669, 2522224, 2110565, 3422321, 3248162, 4891950, 1636924, 2549470, 3069305, 3296688, 2515654, 1813892, 2545292, 3581125, 3040574, 3462141, 1635981, 1639587, 1639624, 1639898, 1639824, 1639839, 1636542, 1636555, 4815173, 1634495, 1616886, 2549206, 1623583, 2543319, 2230130, 1643798, 1645204, 1646087, 1647125, 1626896, 1635369, 1636870, 1639787, 1645928, 1646265, 1635250, 1642621, 1782226, 4858880, 1634907, 1629769, 1630090, 1634473, 2543227, 1634130, 1634774, 1634438, 1620456, 1629501, 1619056, 2241275, 4873006, 3086658, 2495865, 4801756, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200]
    #     members = self.context.get_raw_members(list_id_doc)

    #     members_id_doc = {}
    #     for member in members:
    #         members_id_doc[str(member.id_doc)] = member

    #     if members is None:
    #         raise HTTPNotFound()

    #     documents = self.context.get_full_documents(
    #         list_id_doc, members_id_doc)

    #     return Response(utils.object2json(documents),
    #                    content_type='application/json')



















    def update_collection(self):
        """ 
        Udpdate database collection of objects. This method needs a valid JSON
        query, a valid query path and the object to update. Will query database
        objects, and update each path to the new object. Return count of
        successes and failures.
        """
        self.context.result_count = False
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
