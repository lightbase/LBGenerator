
from pyramid_restler.view import RESTfulView
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from lbgenerator.lib import utils

class CustomView(RESTfulView):

    """ General Customized Views for REST app.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        md = self.request.matchdict
        self.base_name = md.get('base')
        if md.get('id'):
            if not utils.is_integer(md.get('id')):
                raise Exception('id "%s" is not an integer!' %(md.get('id')))

    def get_db_obj(self):
        id = self.request.matchdict['id']
        return self.context.get_member(id)

    def get_member(self):
        id = self.request.matchdict['id']
        self.wrap = False
        member = self.context.get_member(id)
        return self.render_to_response(member)

    def _get_data(self):
        """ Get all valid data from (request) POST or PUT.
        """
        return self.data

    def get_base(self):
        return self.context.get_base()

    def set_base(self, base_json):
        return self.context.set_base(base_json)

    def get_collection(self):
        kwargs = self.request.params.get('$$', {})
        if kwargs:
            kwargs = utils.to_json(kwargs)
        try:
            collection = self.context.get_collection(**kwargs)
            return self.render_to_response(collection)
        except Exception as e:
            raise Exception('Error trying to complete your search: {}'.format(str(e.args[0])))

    def create_member(self):
        member = self.context.create_member(self._get_data())
        id = self.context.get_member_id_as_string(member)
        headers = {'Location': '/'.join((self.request.path, id))}
        return Response(id, status=201, headers=headers)

    def update_member(self, doc_data=None):
        id = self.request.matchdict['id']
        if doc_data:
            data = doc_data
            index = False
        else:
            data = self._get_data()
            index = True
        member = self.context.update_member(id, data, index=index)
        if member is None:
            raise HTTPNotFound()
        else:
            return Response('UPDATED', charset='utf-8', status=200, content_type='')

    def delete_member(self):
        id = self.request.matchdict['id']
        member = self.context.delete_member(id)
        if member is None:
            raise HTTPNotFound()
        return Response('DELETED', charset='utf-8', status=200, content_type='')





