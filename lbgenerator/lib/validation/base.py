
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
        json_base['metadata']['id_base'] = cls.context.get_next_id()
        json_base['metadata']['dt_base'] = datetime.datetime.now()

        base = genesis.json_to_base(json_base)

        data = dict(
            id_base = base.metadata.id_base,
            dt_base = base.metadata.dt_base,
            name = base.metadata.name,
            struct = base.asdict,
            idx_exp = base.metadata.idx_exp,
            idx_exp_url = base.metadata.idx_exp_url,
            idx_exp_time= base.metadata.idx_exp_time,
            file_ext = base.metadata.file_ext,
            file_ext_time = base.metadata.file_ext_time
        )

    if method == 'PUT':
        if not 'json_base' in data:
            raise Exception('Required: json_base')

        json_base = utils.json2object(data['json_base'])

        member = cls.context.get_member(json_base['metadata']['name'])

        json_base['metadata']['id_base'] = member.id_base
        json_base['metadata']['dt_base'] = member.dt_base

        base = cls.set_base(json_base)

        data = dict(
            name = base.metadata.name,
            struct = base.json,
            idx_exp = base.metadata.idx_exp,
            idx_exp_url = base.metadata.idx_exp_url,
            idx_exp_time= base.metadata.idx_exp_time,
            file_ext = base.metadata.file_ext,
            file_ext_time = base.metadata.file_ext_time
        )

    return data
