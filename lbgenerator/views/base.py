
from lbgenerator.views import CustomView
from lbgenerator.lib.validation.base import validate_base_data

class BaseCustomView(CustomView):

    """ Customized views for base REST app.
    """
    def __init__(self, *args):
        super(BaseCustomView, self).__init__(*args)
        self.data = validate_base_data(self, args[1])
