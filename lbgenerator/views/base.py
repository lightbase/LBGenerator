
from lbgenerator.views import CustomView
from lbgenerator.lib.validation.base import validate_base_data

class BaseCustomView(CustomView):

    """ Customized views for base REST app.
    """
    def __init__(self, context, request):
        super(BaseCustomView, self).__init__(context, request)
        self.data = validate_base_data(self, request)
