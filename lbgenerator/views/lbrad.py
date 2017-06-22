import json
import logging

from lbgenerator.lbrad.dispatcher import OperationError
from lbgenerator.lbrad.dispatcher import OperationDispatcher

logger = logging.getLogger("DEBUG")


def dispatch_msg(request):
    dispatcher = OperationDispatcher(request.json_body, request.url)
    try:
        result = dispatcher.dispatch()
    except OperationError as e:
        result = { "error": str(e.msg) }

    # NOTE: Tentar fechar a conexão de qualquer forma!
    # -> Na criação da conexão "coautocommit=True"!
    # By Questor
    try:
        if request.context.session.is_active:
            request.context.session.close()
    except:
        pass

    return result

def dispatch_msg_multipart(request):
    params_json = request.POST['params']

    # TODO: deal with error! By John Doe
    params = json.loads(params_json)

    for key, file in request.POST.items():
        if key.startswith('file_'):

            # NOTE: Add a file to its respective operation in the params dict!
            # By John Doe
            str_index = key.replace('file_', '')

            # TODO: Deal with error! By John Doe
            op_index = int(str_index)

            params['operations'][op_index]['data'] = file

    dispatcher = OperationDispatcher(params, request.url)
    try:
        result = dispatcher.dispatch()
    except OperationError as e:
        result = { "error": str(e.msg) }

    # NOTE: Tentar fechar a conexão de qualquer forma!
    # -> Na criação da conexão "coautocommit=True"!
    # By Questor
    try:
        if request.context.session.is_active:
            request.context.session.close()
    except:
        pass

    return result
