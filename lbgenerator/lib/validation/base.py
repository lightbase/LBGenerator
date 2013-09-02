
from lbgenerator.lib import utils

def validate_base_data(cls, request):
    params, method = utils.split_request(request)
    valid_fields = (
        'id_base',
        'nome_base',
        'xml_base',
        'dt_base'
        )

    data = utils.filter_params(params, valid_fields)

    if method == 'POST':
        if not 'nome_base' in data or not 'xml_base' in data:
            raise Exception('Required: nome_base, xml_base')
        if utils.base_exists(data.get('nome_base')):
            raise Exception('Base already exists!')
        data['dt_base'] = str(datetime.datetime.now())
    return data

    if method == 'PUT':
        raise Exception('Not implemented')
        if data.get('dt_base'): del data['dt_base']
