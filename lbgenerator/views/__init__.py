
from pyramid_restler.view import RESTfulView
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from lbgenerator.model.entities import *
from lbgenerator.model import BASES
from lbgenerator.lib import utils

class CustomView(RESTfulView):

    """ General Customized Views for REST app.
    """
    def __init__(self, *args):
        self.context = args[0]
        self.request = args[1]
        md = self.request.matchdict
        self.base_name = md.get('basename')
        if md.get('id'):
            if not utils.is_integer(md.get('id')):
                raise Exception('id "%s" is not an integer!' %(md.get('id')))

    def get_member(self, render=True):
        id = self.request.matchdict['id']
        if hasattr(self.context.entity, 'json_reg'):
            self.fields = ['json_reg']
        self.wrap = False
        member = self.context.get_member(id)
        if render: return self.render_to_response(member)
        else: return member

    def _get_data(self):
        """ Get all valid data from (request) POST or PUT.
        """
        return self.data

    def get_base(self):
        return BASES.get_base(self.base_name)

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
        if hasattr(self.context, 'delete_referenced_docs'):
            self.context.delete_referenced_docs(id)
        member = self.context.delete_member(id)
        if member is None:
            raise HTTPNotFound()
        return Response('DELETED', charset='utf-8', status=200, content_type='')





