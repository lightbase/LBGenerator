
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import forbidden_view_config
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPForbidden
import traceback
from ..lib import utils
import sys

from ..lib.lb_exception import LbException
from ..lib.utils import LbUseful

class JsonErrorMessage():

    def get_error(self):

        json_error = {
            'status': self.code,
            'type': self.request.exc_info[0].__name__,
            'error_message': self._error_message,
            'request':{
                'client_addr': self.request.client_addr,
                'user_agent': self.request.user_agent,
                'path': getattr(self.request, 'path', 'Not avalible'),
                'method': self.request.method
            },
        }
        if 'verbose' in self.request.params:
            json_error['request']['body'] = str(self.request.text)
        return utils.object2json(json_error)

class JsonHTTPServerError(HTTPInternalServerError, JsonErrorMessage):

    def __init__(self, request, _error_message):
        self._error_message = _error_message
        self.request = request
        Response.__init__(self, self.get_error(), status=self.code)
        self.content_type = 'application/json'

class JsonHTTPNotFound(HTTPNotFound, JsonErrorMessage):

    def __init__(self, request):
        self._error_message = self.title
        self.request = request
        Response.__init__(self, self.get_error(), status=self.code)
        self.content_type = 'application/json'

class JsonHTTPForbidden(HTTPForbidden, JsonErrorMessage):

    def __init__(self, request):
        self._error_message = self.title
        self.request = request
        Response.__init__(self, self.get_error(), status=self.code)
        self.content_type = 'application/json'

@forbidden_view_config()
def forbidden(request):
    """ Customized Forbidden View
    """
    return JsonHTTPForbidden(request)

@view_config(context=NotFound)
def notfound_view(request):
    """ Customized NotFound View
    """
    return JsonHTTPNotFound(request)

@view_config(context=Exception)
def error_view(exc, request):
    """ Customized Exception View
    """
    exc_type, exc_obj, exc_tb = sys.exc_info()
    exc_msg = exc_obj.args
    if len(exc_obj.args) > 0:
        exc_msg = exc_obj.args[0]
    tb_list = traceback.format_tb(exc_tb)
    str_msg = str(exc_msg) + ' ' + ''.join(tb_list)
    return JsonHTTPServerError(request, str_msg)

@view_config(context=LbException)
def lbexception_view(exc, request):
    """
    Trata-se de um view customizada para os erros do LightBase.
    """
    exc_type, exc_obj, exc_tb = sys.exc_info()
    exc_msg = exc_obj.args
    if len(exc_obj.args) > 0:
        exc_msg = exc_obj.args[0]
    return JsonHTTPServerError(request, str(exc_msg))
