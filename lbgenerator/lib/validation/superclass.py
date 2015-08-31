
from ..exceptions import RequiredParameterError


class RequestValidation(object):

    """ HTTP request validation properties and methods
    """

    def __init__(self, view, request):
        """ Class constructor
        """
        # @property view:
        self.view = view

        # @property params:
        self.params = request.params

        # @property method:
        self.method = request.method

    def get_valid_data(self):
        """ Get valid data according to HTTP method.
        """
        return getattr(self, self.method.lower())()

    def verify_param(self, param, type_):
        """
        @param param:
        @param type_:
        """
        try:
            msg = 'Required parameter %s not found in request' % param
            assert param in self.params, msg
        except AssertionError as e:
            raise RequiredParameterError(e)

        try:
            msg = 'Parameter %s must be instance of %s.' % (param, type_)
            assert isinstance(self.params[param], type_), msg
        except AssertionError as e:
            raise TypeError(e)

        else:
            return self.params[param]
