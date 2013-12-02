
from pyramid.response import Response
from lbgenerator.views import CustomView
from lbgenerator.lib.validation.base import validate_base_data
from pyramid.exceptions import HTTPNotFound

class BaseCustomView(CustomView):

    """ Base Customized View Methods
    """
    def __init__(self, context, request):
        super(BaseCustomView, self).__init__(context, request)
        self.data = validate_base_data(self, request)
