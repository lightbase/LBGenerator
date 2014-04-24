
from lbgenerator.views import CustomView
from lbgenerator.lib.validation.base import validate_base_data
from lbgenerator.lib import utils
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
import json

class BaseCustomView(CustomView):

    """ Base Customized View Methods
    """
    def __init__(self, context, request):
        super(BaseCustomView, self).__init__(context, request)

    def _get_data(self):
        """ Get all valid data from (request) POST or PUT.
        """
        return validate_base_data(self, self.request)

    def get_member(self):
        self.wrap = False
        base = self.request.matchdict['base']
        member = self.context.get_member(base)
        return self.render_to_response(member)

    def update_member(self):
        base = self.request.matchdict['base']
        member = self.context.update_member(base, self._get_data())
        if member is None:
            raise HTTPNotFound()
        else:
            return Response('UPDATED', charset='utf-8', status=200, content_type='')

    def delete_member(self):
        base = self.request.matchdict['base']
        member = self.context.delete_member(base)
        if member is None:
            raise HTTPNotFound()
        return Response('DELETED', charset='utf-8', status=200, content_type='')

    def get_column(self):
        """ Get column value
        """
        base = self.request.matchdict['base']
        PATH = self.request.matchdict['column'].split('/')
        column = PATH.pop(0)

        member = self.context.get_member(base)
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
