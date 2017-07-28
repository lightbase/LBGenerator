import sys
import traceback

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.exceptions import NotFound
from pyramid.view import forbidden_view_config
from pyramid.httpexceptions import HTTPConflict
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPInternalServerError

from ..lib import utils
from ..lib.utils import LbUseful
from ..lib.lb_exception import LbException


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

        # NOTE I: Pode parecer excesso de zelo... Mas, mesmo não havendo,
        # necessariamente, "views" para esses métodos eu optei por tentar
        # fechar a conexão AQUI TAMBÉM para garantir que um "raise exception"
        # da vida impeça a conexão de ser fechada! By Questor

        # NOTE II: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if request.context.session.is_active:
                request.context.session.close()
        except:
            pass

        return utils.object2json(json_error)

class JsonHTTPServerError(HTTPInternalServerError, JsonErrorMessage):

    def __init__(self, request, _error_message):

        # NOTE I: Pode parecer excesso de zelo... Mas, mesmo não havendo,
        # necessariamente, "views" para esses métodos eu optei por tentar
        # fechar a conexão AQUI TAMBÉM para garantir que um "raise exception"
        # da vida impeça a conexão de ser fechada! By Questor

        # NOTE II: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if request.context.session.is_active:
                request.context.session.close()
        except:
            pass

        self._error_message = _error_message
        self.request = request
        Response.__init__(self, self.get_error(), status=self.code)
        self.content_type = 'application/json'

class JsonHTTPNotFound(HTTPNotFound, JsonErrorMessage):

    def __init__(self, request):

        # NOTE I: Pode parecer excesso de zelo... Mas, mesmo não havendo,
        # necessariamente, "views" para esses métodos eu optei por tentar
        # fechar a conexão AQUI TAMBÉM para garantir que um "raise exception"
        # da vida impeça a conexão de ser fechada! By Questor

        # NOTE II: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if request.context.session.is_active:
                request.context.session.close()
        except:
            pass

        self._error_message = self.title
        self.request = request
        Response.__init__(self, self.get_error(), status=self.code)
        self.content_type = 'application/json'

class JsonHTTPForbidden(HTTPForbidden, JsonErrorMessage):

    def __init__(self, request):

        # NOTE I: Pode parecer excesso de zelo... Mas, mesmo não havendo,
        # necessariamente, "views" para esses métodos eu optei por tentar
        # fechar a conexão AQUI TAMBÉM para garantir que um "raise exception"
        # da vida impeça a conexão de ser fechada! By Questor

        # NOTE II: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if request.context.session.is_active:
                request.context.session.close()
        except:
            pass

        self._error_message = self.title
        self.request = request
        Response.__init__(self, self.get_error(), status=self.code)
        self.content_type = 'application/json'

class JsonHTTPConflict(HTTPConflict, JsonErrorMessage):

    def __init__(self, request, _error_message):

        # NOTE I: Pode parecer excesso de zelo... Mas, mesmo não havendo,
        # necessariamente, "views" para esses métodos eu optei por tentar
        # fechar a conexão AQUI TAMBÉM para garantir que um "raise exception"
        # da vida impeça a conexão de ser fechada! By Questor

        # NOTE II: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if request.context.session.is_active:
                request.context.session.close()
        except:
            pass

        self._error_message = _error_message
        self.request = request
        Response.__init__(self, self.get_error(), status=self.code)
        self.content_type = 'application/json'

@forbidden_view_config()
def forbidden(request):
    """ Customized Forbidden View
    """

    # NOTE I: Pode parecer excesso de zelo... Mas, mesmo não havendo,
    # necessariamente, "views" para esses métodos eu optei por tentar fechar a
    # conexão AQUI TAMBÉM para garantir que um "raise exception" da vida impeça
    # a conexão de ser fechada! By Questor

    # NOTE II: Tentar fechar a conexão de qualquer forma!
    # -> Na criação da conexão "coautocommit=True"!
    # By Questor
    try:
        if request.context.session.is_active:
            request.context.session.close()
    except:
        pass

    return JsonHTTPForbidden(request)

@view_config(context=NotFound)
def notfound_view(request):
    """ Customized NotFound View
    """

    # NOTE I: Pode parecer excesso de zelo... Mas, mesmo não havendo,
    # necessariamente, "views" para esses métodos eu optei por tentar fechar a
    # conexão AQUI TAMBÉM para garantir que um "raise exception" da vida impeça
    # a conexão de ser fechada! By Questor

    # NOTE II: Tentar fechar a conexão de qualquer forma!
    # -> Na criação da conexão "coautocommit=True"!
    # By Questor
    try:
        if request.context.session.is_active:
            request.context.session.close()
    except:
        pass

    return JsonHTTPNotFound(request)

@view_config(context=Exception)
def error_view(exc, request):
    """ Customized Exception View
    """

    exc_type, exc_obj, exc_tb = sys.exc_info()
    exc_msg = exc_obj.args
    if len(exc_obj.args) > 0:
        exc_msg = exc_obj.args[0]

    # NOTE I: Pode parecer excesso de zelo... Mas, mesmo não havendo,
    # necessariamente, "views" para esses métodos eu optei por tentar fechar a
    # conexão AQUI TAMBÉM para garantir que um "raise exception" da vida impeça
    # a conexão de ser fechada! By Questor

    # NOTE II: Tentar fechar a conexão de qualquer forma!
    # -> Na criação da conexão "coautocommit=True"!
    # By Questor
    try:
        if request.context.session.is_active:
            request.context.session.close()
    except:
        pass

    return JsonHTTPServerError(request, str(exc_msg))

@view_config(context=LbException)
def lbexception_view(exc, request):
    """
    Trata-se de um view customizada para os erros do LightBase.
    """

    exc_type, exc_obj, exc_tb = sys.exc_info()
    exc_msg = exc_obj.args
    if len(exc_obj.args) > 0:
        exc_msg = exc_obj.args[0]

    # NOTE I: Pode parecer excesso de zelo... Mas, mesmo não havendo,
    # necessariamente, "views" para esses métodos eu optei por tentar fechar a
    # conexão AQUI TAMBÉM para garantir que um "raise exception" da vida impeça
    # a conexão de ser fechada! By Questor

    # NOTE II: Tentar fechar a conexão de qualquer forma!
    # -> Na criação da conexão "coautocommit=True"!
    # By Questor
    try:
        if request.context.session.is_active:
            request.context.session.close()
    except:
        pass

    return JsonHTTPServerError(request, str(exc_msg))

@view_config(context=HTTPConflict)
def conflict_view(exc, request):
    """
    View that responds to HTTPConflict errors.
    """

    exc_type, exc_obj, exc_tb = sys.exc_info()
    exc_msg = exc_obj.args
    if len(exc_obj.args) > 0:
        exc_msg = exc_obj.args[0]

    # NOTE I: Pode parecer excesso de zelo... Mas, mesmo não havendo,
    # necessariamente, "views" para esses métodos eu optei por tentar fechar a
    # conexão AQUI TAMBÉM para garantir que um "raise exception" da vida impeça
    # a conexão de ser fechada! By Questor

    # NOTE II: Tentar fechar a conexão de qualquer forma!
    # -> Na criação da conexão "coautocommit=True"!
    # By Questor
    try:
        if request.context.session.is_active:
            request.context.session.close()
    except:
        pass

    return JsonHTTPConflict(request, str(exc_msg))

