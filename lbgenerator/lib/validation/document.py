
import datetime
import cgi
from lbgenerator.lib import utils
from pyramid.exceptions import NotFound

def validate_doc_data(cls, request):

    params, method = utils.split_request(request)
    if method == 'GET': return None

    valid_fields = (
        '_field_name_',
        'id_doc',
        'id_reg',
        'grupos_acesso',
        'nome_doc',
        'blob_doc',
        'mimetype',
        'texto_doc',
        'dt_ext_texto',
        )

    def has_doc(params):
        for k, v in params.items():
            if isinstance(v, cgi.FieldStorage): return True
        return False

    def get_doc(params):
        _data = dict()
        ct = 0
        for k, v in params.items():
            if isinstance(v, cgi.FieldStorage):
                ct += 1
                _data = dict(
                    _field_name_ = k,
                    nome_doc = v.filename,
                    mimetype = v.type,
                    blob_doc = v.file.read()
                    )
        if ct > 1:
            raise Exception('Forbidden: More than one document per request')
        return _data

    data = params

    if method == 'POST':
        pass
        """
        if not 'id_reg' in params:
            raise Exception('Required param: id_reg')
        cls.id_reg = params['id_reg']
        cls.set_json_reg()
        data.update(get_doc(params))
        """

    elif method == 'PUT':
        pass
        """
        if has_doc(params):
            if not 'id_reg' in params:
                raise Exception('Trying to insert a new doc? Param "id_reg" is required!')
            else:
                cls.id_reg = params['id_reg']
                cls.set_json_reg()
                data.update(get_doc(params))
        data['dt_ext_texto'] = None
        data['texto_doc'] = None
        """

    return utils.filter_params(data, valid_fields)
