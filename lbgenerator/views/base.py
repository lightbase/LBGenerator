
from . import CustomView
from ..lib.validation.base import validate_base_data
from ..lib import utils
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from beaker.cache import cache_region
from ..lib import cache


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

        # Clear cache
        cache.clear_cache()
        return Response('DELETED', charset='utf-8', status=200, content_type='')

    def get_column(self):
        """ Get column value
        """
        base = self.request.matchdict['base']
        PATH = self.request.matchdict['column'].split('/')
        base = self.context.get_base()
        value = base.asdict

        for path_name in PATH:
            try: path_name = int(path_name)
            except: pass
            try:
                if isinstance(value, list) and isinstance(path_name, int):
                    value = value[path_name]
                elif path_name in value:
                    value = value[path_name]
                else:
                    value = base.get_struct(path_name).asdict
            except Exception as e:
                raise Exception(e)

        value = utils.object2json(value)
        return Response(value, content_type='application/json')
