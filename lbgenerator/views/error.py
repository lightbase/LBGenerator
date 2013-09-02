
from pyramid.response import Response
from pyramid.view import view_config
import json
from pyramid.exceptions import NotFound
import traceback

def json_msg(status=None, err_msg=None, request=None):
    try: req = str(request)
    except: req = 'Request Object'
    msg = dict(
        _status=status,
        _error_message=err_msg,
        _path=getattr(request, 'path', None),
        _request=req
        )
    return Response(json.dumps(msg), content_type='application/json')

@view_config(context=NotFound)
def notfound_view(request):
    """ Customized NotFound view for Rest Api
    """
    try: req = str(request)
    except Exception as e: req=e
    return json_msg(404, 'Not Found', req)

@view_config(context=Exception)
def error_view(exc, request):
    """ Customized view for thowing RestExceptions
        Prints error exceptions into log file
    """
    print(traceback.format_exc())
    if type(exc.args) is tuple or type(exc.args) is list:
        em = str(exc.args[0])
    else:
        em = str(exc.args)
    return json_msg(500, em, request)
