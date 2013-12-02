
from pyramid_restler.view import RESTfulView
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from lbgenerator.lib import utils
import json

class CustomView(RESTfulView):

    """ Default Customized View Methods
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.base_name = self.request.matchdict.get('base')
        if self.request.matchdict.get('id'):
            id = self.request.matchdict['id']
            if not utils.is_integer(id):
                raise Exception('id "%s" is not an integer!' % id)

    def get_db_obj(self):
        id = self.request.matchdict['id']
        return self.context.get_member(id)

    def get_column(self):
        """ Get column value
        """
        id = self.request.matchdict['id']
        column = self.request.matchdict['column']
        if column == 'blob_doc':
            location = self.request.path.replace('blob_doc', 'download')
            return HTTPFound(location=location)
        member = self.context.get_member(id)
        if member is None:
            return HTTPNotFound()

        if type(member) is list: member = member[0]
        try: value = getattr(member, column)
        except: raise Exception('Could not find column %s' % column)

        try: value = utils.to_json(value)
        except: pass

        value = json.dumps(value, cls=self.context.json_encoder, ensure_ascii=False)
        return Response(str(value), charset='utf-8', status=200, content_type='')

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
        """ Return Base object
        """
        return self.context.get_base()

    def set_base(self, base_json):
        """ Set Base object
        """
        return self.context.set_base(base_json)

    def get_collection(self):
        """ Search database objects
        """
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

    def update_member(self):
        id = self.request.matchdict['id']
        member = self.context.update_member(id, self._get_data())
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





