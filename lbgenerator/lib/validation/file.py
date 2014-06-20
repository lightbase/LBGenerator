
from .. import utils
from pyramid.exceptions import NotFound
import cgi

def validate_file_data(cls, request):

    params, method = utils.split_request(request)
    if method == 'GET': return None

    return params
