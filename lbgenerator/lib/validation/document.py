import datetime

from .. import utils
from liblightbase.lbtypes import Matrix
from liblightbase.lbdoc.metadata import DocumentMetadata

def validate_document_data(cls, request, *args):
    params, method = utils.split_request(request)
    if method == 'GET': return None

    valid_fields = (
        'value',
        'dt_idx',
        'validate'
        )

    data = utils.filter_params(params, valid_fields)

    if method == 'POST':
        return validate_post_data(cls, data)
    elif method == 'PUT':
        member = args[0]
        return validate_put_data(cls, data, member)
    elif method == 'PATCH':
        member = args[0]
        whole_doc = True
        if len(args) > 1:
            whole_doc = args[1]
        return validate_patch_data(cls, data, member, whole_doc)

def validate_post_data(cls, data):
    validate = True

    if 'validate' in data and data['validate'] == '0':
        validate = False

    if 'value' in data:
        # Get Base object
        base = cls.get_base()

        # Parse JSON object
        document = utils.json2object(data['value'])

        # SELECT next id from sequence
        id = cls.context.entity.next_id()

        # Build Metadata
        now = datetime.datetime.now()
        _metadata = DocumentMetadata(id, now, now)

        (document, # Document it self.
        reldata, # Relational data.
        files, # All existent files within document.
        cfiles # All non-existent (will be created) files within document.
        ) = base.validate(document, _metadata, validate)

        # Normlize relational data
        [fix_matrix(reldata[field]) for field in reldata if isinstance(reldata[field], Matrix)]

        # Build database object
        data['document'] = document
        data['__files__'] = files
        data.update(_metadata.__dict__)
        data.update(reldata)

    return data

def validate_put_data(cls, data, member):
    validate = True

    if 'validate' in data and data['validate'] == '0':
        validate = False
        data.pop('validate')

    if 'value' in data:

        # NOTE: Recupera a estrutura (json) da base no formato dict.
        # Get Base object (CustomView <- DocumentContextFactory <-
        # CustomContextFactory <- BaseMemory <- get_base())
        base = cls.get_base()

        # Parse JSON object
        document = utils.json2object(data['value'])
        data.pop('value')

        dt_idx = document.get('_metadata', { })\
                .get('dt_idx', None)

        if dt_idx and not isinstance(dt_idx, datetime.datetime):
            dt_idx = datetime.datetime.strptime(
                dt_idx, '%d/%m/%Y %H:%M:%S')

        # Build Metadata
        _metadata = DocumentMetadata(**dict(
            id_doc = member.id_doc,
            dt_doc = member.dt_doc,
            dt_last_up = datetime.datetime.now(),
            dt_idx = dt_idx,
            dt_del = member.dt_del
        ))

        (document, # Document it self.
        reldata, # Relational data.
        files, # All existent files within document.
        cfiles # All non-existent (will be created) files within document.
        ) = base.validate(document, _metadata, validate)

        # Normalize relational data
        [fix_matrix(reldata[field]) for field in reldata if isinstance(reldata[field], Matrix)]

        # Build database object
        data['document'] = document
        data['__files__'] = files
        data.update(_metadata.__dict__)
        data.update(reldata)

    return data

def validate_patch_data(cls, data, member, whole_doc=True):
    validate = True

    if 'validate' in data and data['validate'] == '0':
        validate = False
        data.pop('validate')

    if 'value' in data:
        # NOTE: Recupera a estrutura (json) da base no formato dict.
        # Get Base object (CustomView <- DocumentContextFactory <-
        # CustomContextFactory <- BaseMemory <- get_base())
        base = cls.get_base()

        # Parse JSON object
        if not whole_doc:
            document = member.document
            updated_partial_document = utils.json2object(data['value'])    
            # update member.document with new data
            utils.DocumentPatchUtils().update_dict(document, updated_partial_document)
        else:
            document = utils.json2object(data['value'])

        data.pop('value')

        dt_idx = document.get('_metadata', {}).get('dt_idx', None)
        if dt_idx and not isinstance(dt_idx, datetime.datetime):
            dt_idx = datetime.datetime.strptime(
                dt_idx, '%d/%m/%Y %H:%M:%S')

        # Build Metadata
        _metadata = DocumentMetadata(**dict(
            id_doc=member.id_doc,
            dt_doc=member.dt_doc,
            dt_last_up=datetime.datetime.now(),
            dt_idx=dt_idx,
            dt_del=member.dt_del
        ))

        (document, # Document it self.
        reldata, # Relational data.
        files, # All existent files within document.
        cfiles # All non-existent (will be created) files within document.
        ) = base.validate(document, _metadata, validate)

        # Normalize relational data
        [fix_matrix(reldata[field]) for field in reldata if isinstance(reldata[field], Matrix)]

        # Build database object
        data['document'] = document
        data['__files__'] = files
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
