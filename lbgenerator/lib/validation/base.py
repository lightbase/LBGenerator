
from liblightbase.lbbase import genesis
from lbgenerator.lib import utils
import datetime
import json

def validate_base_data(cls, request):
    params, method = utils.split_request(request)
    valid_fields = (
        'id_base',
        'nome_base',
        'json_base',
        'dt_base',
        'reg_model',
        'password',
        'index_export',
        'index_url',
        'index_time',
        'doc_extract',
        'extract_time'
        )

    data = utils.filter_params(params, valid_fields)
    if method == 'POST':
        if not 'json_base' in data:
            raise Exception('Required: json_base')
        json_base = utils.json2object(data['json_base'])
        base = genesis.json_to_base(json_base)
        data = dict(
            nome_base = base.name,
            json_base = base.json,
            reg_model = base.reg_model,
            dt_base = str(datetime.datetime.now()),
            password = base.password,
            index_export = base.index_export,
            index_url = base.index_url,
            index_time= base.index_time,
            doc_extract = base.doc_extract,
            extract_time = base.extract_time
        )

    if method == 'PUT':
        if not 'json_base' in data:
            raise Exception('Required: json_base')
        json_base = utils.json2object(data['json_base'])
        base = cls.set_base(json_base)
        data = dict(
            nome_base = base.name,
            json_base = base.json,
            reg_model = base.reg_model,
            password = base.password,
            index_export = base.index_export,
            index_url = base.index_url,
            index_time= base.index_time,
            doc_extract = base.doc_extract,
            extract_time = base.extract_time
        )

    return data
