
from lbgenerator.lib import utils
import datetime

def validate_base_data(cls, request):
    params, method = utils.split_request(request)
    valid_fields = (
        'id_base',
        'nome_base',
        'json_base',
        'dt_base'
        )

    data = utils.filter_params(params, valid_fields)

    if method == 'POST':
        #TODO: verify if base already exists
        if not 'json_base' in data:
            raise Exception('Required: json_base')
        data['dt_base'] = str(datetime.datetime.now())
        return data

    if method == 'PUT':
        if not 'json_base' in data:
            raise Exception('Required: json_base')
        if data.get('dt_base'):
            del data['dt_base']
        return data
        





