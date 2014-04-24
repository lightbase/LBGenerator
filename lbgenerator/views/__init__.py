
from pyramid_restler.view import RESTfulView
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from lbgenerator.lib import utils
import json

def response_callback(request, response):
    if 'callback' in request.params:
        response.text = request.params['callback'] + '(' + response.text + ')'

class CustomView(RESTfulView):

    """ Default Customized View Methods
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.add_response_callback(response_callback)
        self.base_name = self.request.matchdict.get('base')
        if self.request.matchdict.get('id'):
            id = self.request.matchdict['id']
            if not utils.is_integer(id):
                raise Exception('id "%s" is not an integer!' % id)

    def get_db_obj(self):
        id = self.request.matchdict['id']
        member = self.context.get_member(id)
        if member is None:
            raise HTTPNotFound()
        return member

    def get_column(self):
        """ Get column value
        """
        id = self.request.matchdict['id']
        PATH = self.request.matchdict['column'].split('/')
        column = PATH.pop(0)

        member = self.context.get_member(id)
        if member is None:
            raise HTTPNotFound()

        if type(member) is list: member = member[0]
        try: value = getattr(member, column)
        except: raise Exception('Could not find column %s' % column)

        try: value = utils.json2object(value)
        except: pass

        if PATH:
            for path_name in PATH:
                try: path_name = int(path_name)
                except: pass
                try: value = value[path_name]
                except:
                    raise Exception('Invalid attribute "%s"' % path_name)

        value = json.dumps(value, cls=self.context.json_encoder, ensure_ascii=False)
        return Response(body=value, content_type='application/json')

    def get_base(self):
        """ Return Base object
        """
        return self.context.get_base()

    def set_base(self, base_json):
        """ Set Base object
        """
        return self.context.set_base(base_json)

    def get_collection(self, render_to_response=True):
        """ Search database objects
        """
        params = self.request.params.get('$$', '{}')
        query = utils.json2object(params)
        try:
            collection = self.context.get_collection(query)
        except Exception as e:
            raise Exception('SearchError: %s' % e)
        if render_to_response:
            response = self.render_to_response(collection)
        else:
            response = collection
        return response

    def get_member(self):
        id = self.request.matchdict['id']
        self.wrap = False
        member = self.context.get_member(id)
        return self.render_to_response(member)

    def create_member(self):
        member = self.context.create_member(self._get_data())
        id = self.context.get_member_id_as_string(member)
        return self.render_custom_response(id, default_response=id)

    def update_member(self):
        id = self.request.matchdict['id']
        member = self.context.get_member(id)
        if member is None:
            raise HTTPNotFound()
        self.context.update_member(member, self._get_data(member))
        return self.render_custom_response(id, default_response='UPDATED')

    def delete_member(self):
        id = self.request.matchdict['id']
        member = self.context.delete_member(id)
        if member is None:
            raise HTTPNotFound()
        return Response('DELETED', charset='utf-8', status=200, content_type='')

    def render_custom_response(self, id, default_response):
        _return = self.request.params.get('return', '')
        is_valid_return = hasattr(self.context.entity, _return)
        if is_valid_return:
            member = self.context.get_member(id)
            response_attr = getattr(member, _return)
            return Response(str(response_attr), charset='utf-8', status=200, content_type='application/json')
        else:
            return Response(default_response, charset='utf-8', status=200, content_type='')





