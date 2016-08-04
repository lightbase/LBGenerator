import logging
import json
from lbgenerator.lbrad.dispatcher import OperationDispatcher
from lbgenerator.lbrad.dispatcher import OperationError

logger = logging.getLogger("DEBUG")

def dispatch_msg(request):
    dispatcher = OperationDispatcher(request.json_body, request.url)

    logger.debug("Dispatcher - before")
  
    try:
        result = dispatcher.dispatch()
    except OperationError as e:
        logger.debug("Dispatcher - error: " + str(e.msg))
        result = { "error": str(e.msg) }

    logger.debug("Dispatcher - after")
    logger.debug("Dispatcher - result = " + str(result))

    return result

def dispatch_msg_multipart(request):
    params_json = request.POST['params']
    # TODO: deal with error
    params = json.loads(params_json)  

    for key, file in request.POST.items():
        if key.startswith('file_'):
            # add a file to its respective operation in the params dict
            str_index = key.replace('file_', '')
            # TODO: deal with error
            op_index = int(str_index)
            params['operations'][op_index]['data'] = file


    dispatcher = OperationDispatcher(params, request.url)

    logger.debug("Dispatcher - before")
  
    try:
        result = dispatcher.dispatch()
    except OperationError as e:
        logger.debug("Dispatcher - error: " + str(e.msg))
        result = { "error": str(e.msg) }

    logger.debug("Dispatcher - after")
    logger.debug("Dispatcher - result = " + str(result))

    return result