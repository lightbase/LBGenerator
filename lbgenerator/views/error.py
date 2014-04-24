
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import forbidden_view_config
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPForbidden
import traceback
import json
import sys 

class JsonErrorMessage():

    def get_error(self):
        return json.dumps(dict(
            _status = self.code,
            _error_message = self._error_message,
            _request = self.get_request_str(),
            _path = getattr(self.request, 'path', None)
        ))

    def get_request_str(self):
        try: return str(self.request)
        except: return str()

class JsonHTTPServerError(HTTPInternalServerError, JsonErrorMessage):

    def __init__(self, request, _error_message):
        print(traceback.format_exc())
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
    return JsonHTTPServerError(request, str(exc_msg))

