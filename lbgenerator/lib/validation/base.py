
from liblightbase.lbbase import genesis
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
        if not 'json_base' in data:
            raise Exception('Required: json_base')
        json_base = utils.to_json(data['json_base'])
        base = genesis.json_to_base(json_base)
        data = dict(
            nome_base = base.name,
            json_base = base.json,
            reg_model = str(base.schema.schema),
            dt_base = str(datetime.datetime.now())
        )

    if method == 'PUT':
        if not 'json_base' in data:
            raise Exception('Required: json_base')
        json_base = utils.to_json(data['json_base'])
        base = genesis.json_to_base(json_base)
        data = dict(
            nome_base = base.name,
            json_base = base.json,
            reg_model = str(base.schema.schema),
        )

    return data

        





