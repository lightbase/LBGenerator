
from pyramid.response import Response
from lbgenerator.views import CustomView
from lbgenerator.lib.validation.base import validate_base_data
from pyramid.exceptions import HTTPNotFound

class BaseCustomView(CustomView):

    """ Customized views for base REST app.
    """
    def __init__(self, context, request):
        super(BaseCustomView, self).__init__(context, request)
        self.data = validate_base_data(self, request)

    def update_member(self, doc_data=None):
        id = self.request.matchdict['id']
        data = self._get_data()
        member = self.context.update_member(id, data)
        if member is None:
            raise HTTPNotFound()
        else:
            return Response('UPDATED', charset='utf-8', status=200, content_type='')
