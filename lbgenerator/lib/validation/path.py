
from .. import utils
import datetime

def validate_path_data(request):

    params, method = utils.split_request(request)
    if method == 'GET':
        return None
    return params
