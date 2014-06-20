
from .. import utils
import datetime

def validate_user_data(cls, request, id=None):


    params, method = utils.split_request(request)
    if method == 'GET': return None
    return dict(request.params)

    valid_fields = (
        #'id_user',
        'nm_user',
        'email_user',
        'passwd_user',
        )

    data = utils.filter_params(params, valid_fields)

    if method == 'POST':
        return validate_post_data(cls, data)

    elif method == 'PUT':
        if not id: id = int(request.matchdict['id'])
        return validate_put_data(cls, data, id)

def validate_post_data(cls, data):
    if not 'nm_user' in data:
        raise Exception("param 'nm_user' not found in request")
    if not 'email_user' in data:
        raise Exception("param 'email_user' not found in request")
    if not 'passwd_user' in data:
        raise Exception("param 'passwd_user' not found in request")
    data['js_auth'] = '[]'
    data['dt_cad'] = datetime.datetime.now()
    data['in_active'] = True
    return data

def validate_put_data(cls, data, id):

    return data
