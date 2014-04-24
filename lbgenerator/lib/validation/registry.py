
import json
import datetime
from lbgenerator.lib import utils
from liblightbase.lbtypes import Matrix
from liblightbase.lbregistry import RegistryMetadata

def validate_reg_data(cls, request, *args):

    params, method = utils.split_request(request)
    if method == 'GET': return None

    valid_fields = (
        #'id_reg',
        'json_reg',
        'grupos_acesso',
        #'dt_reg',
        'dt_reg_del',
        'dt_index_rel',
        'dt_index_tex',
        'dt_index_sem',
        'return'
        )

    data = utils.filter_params(params, valid_fields)

    if method == 'POST':
        return validate_post_data(cls, data)

    elif method == 'PUT':
        member = args[0]
        return validate_put_data(cls, data, member)

def validate_post_data(cls, data):

    for key in data:
        if key != 'json_reg':
            try: data[key] = utils.json2object(data[key])
            except: pass

    if 'json_reg' in data:
        # Get Base object
        base = cls.get_base()

        # Parse JSON object
        registry = utils.json2object(data['json_reg'])

        # SELECT next id from sequence
        id = cls.context.entity.next_id()

        # Build Metadata
        now = datetime.datetime.now()
        _metadata = RegistryMetadata(id, now, now)

        # Validate Registry
        registry, reldata, docs = base.validate(registry, _metadata)

        # Normlize relational data
        [fix_matrix(reldata[field]) for field in reldata if isinstance(reldata[field], Matrix)]

        # Build database object
        data['json_reg'] = registry
        data['__docs__'] = docs
        data.update(_metadata.__dict__)
        data.update(reldata)

    return data

def validate_put_data(cls, data, member):

    for key in data:
        if key != 'json_reg':
            try: data[key] = utils.json2object(data[key])
            except: pass

    if 'json_reg' in data:

        # Get Base object
        base = cls.get_base()

        # Parse JSON object
        registry = utils.json2object(data['json_reg'])

        # Build Metadata
        _metadata = RegistryMetadata(**dict(
            id_reg = member.id_reg,
            dt_reg = member.dt_reg,
            dt_last_up = datetime.datetime.now(),
            dt_index_tex = None,
            dt_reg_del = member.dt_reg_del
        ))

        # Validate Registry
        registry, reldata, docs = base.validate(registry, _metadata)

        # Normalize relational data
        [fix_matrix(reldata[field]) for field in reldata if isinstance(reldata[field], Matrix)]

        # Build database object
        data['json_reg'] = registry
        data['__docs__'] = docs
        data.update(_metadata.__dict__)
        data.update(reldata)

    return data

def fix_matrix(mat):
    inner_lens = [len(mat[i]) for i, v in enumerate(mat) if isinstance(mat[i], Matrix)]
    for i, v in enumerate(mat):
        if type(mat[i]) is type(None) and len(inner_lens) > 0:
            mat[i] = [None] * max(inner_lens)
        elif isinstance(mat[i], Matrix):
            if len(mat[i]) < max(inner_lens):
                [mat[i].append(None) for _ in range(max(inner_lens)-len(mat[i]))]
            fix_matrix(mat[i])

