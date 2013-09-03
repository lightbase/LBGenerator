
import json
import datetime
from lbgenerator.lib import utils

def validate_reg_data(cls, request):

    params, method = utils.split_request(request)
    if method == 'GET': return None

    valid_fields = (
        'id_reg',
        'json_reg',
        'grupos_acesso',
        'dt_reg',
        'dt_reg_del',
        'dt_index_rel',
        'dt_index_tex',
        'dt_index_sem'
        )

    data = utils.filter_params(params, valid_fields)

    if method == 'POST':
        data['dt_reg'] = datetime.datetime.now()
        data['id_reg'] = cls.context._execute(cls.seq)
        json_reg = utils.to_json(data.get('json_reg'))

        base = cls.get_base()
        utils.sincronize(json_reg, base.schema)

        data['json_reg'] = json.dumps(cls.set_id_up(json_reg, data['id_reg']), ensure_ascii=False)
        data.update(cls.get_cc_data(json_reg))

    elif method == 'PUT':

        if 'json_reg' in data:
            json_reg = utils.to_json(data['json_reg'])

            base = cls.get_base()
            utils.sincronize(json_reg, base.schema)

            data['json_reg'] = json.dumps(
                cls.set_id_up(json_reg, int(request.matchdict['id'])),
                ensure_ascii=False
            )

            data.update(cls.get_cc_data(json_reg))
            if not 'dt_index_tex' in data:
                data['dt_index_tex'] = None

    return data
