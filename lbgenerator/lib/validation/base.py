
from .. import utils
from liblightbase.lbbase import genesis
import datetime

def validate_base_data(cls, request):
    params, method = utils.split_request(request)
    valid_fields = (
        'json_base',
        )

    data = utils.filter_params(params, valid_fields)
    if method == 'POST':
        if not 'json_base' in data:
            raise Exception('Required: json_base')

        json_base = utils.json2object(data['json_base'])

        base = genesis.json_to_base(json_base)
        base.id_base = cls.context.get_next_id()
        base.dt_base = datetime.datetime.now()

        data = dict(
            id_base = base.id_base,
            dt_base = base.dt_base,
            name = base.name,
            struct = base.json,
            idx_exp = base.idx_exp,
            idx_exp_url = base.idx_exp_url,
            idx_exp_time= base.idx_exp_time,
            file_ext = base.file_ext,
            file_ext_time = base.file_ext_time
        )

    if method == 'PUT':
        if not 'json_base' in data:
            raise Exception('Required: json_base')

        json_base = utils.json2object(data['json_base'])
        base = cls.set_base(json_base)

        member = cls.context.get_member(base.name)
        base.id_base = member.id_base
        base.dt_base = member.dt_base

        data = dict(
            name = base.name,
            struct = base.json,
            idx_exp = base.idx_exp,
            idx_exp_url = base.idx_exp_url,
            idx_exp_time= base.idx_exp_time,
            file_ext = base.file_ext,
            file_ext_time = base.file_ext_time
        )

    return data
