from lbgenerator.model import get_bases
from pyramid.response import Response
from pyramid.view import view_config
import json, datetime, cgi
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
from liblightbase.lbbase.xml import xml_to_base
from pyramid.exceptions import NotFound
import traceback
from pyramid.view import forbidden_view_config
import voluptuous

def json_msg(status=None, err_msg=None, request=None):
    try: req = str(request)
    except: req = 'Request Object'
    msg = dict(
        _status=status,
        _error_message=err_msg,
        _path=getattr(request, 'path', None),
        _request=req
        )
    return Response(json.dumps(msg), content_type='application/json')

@view_config(context=NotFound)
def notfound_view(request):
    """ Customized NotFound view for Rest Api
    """
    try: req = str(request)
    except Exception as e: req=e
    return json_msg(404, 'Not Found', req)

@view_config(context=Exception)
def error_view(exc, request):
    """ Customized view for thowing RestExceptions
        Prints error exceptions into log file
    """
    print(traceback.format_exc())
    if type(exc.args) is tuple or type(exc.args) is list:
        em = str(exc.args[0])
    else:
        em = str(exc.args)
    return json_msg(500, em, request)

@forbidden_view_config()
def forbidden_view(request):
    return json_msg(403, 'Access was denied to this resource.', request)

class RestException(Exception):
    """ Handles and validates erros or exceptions for REST api.
    """

    def __init(self, msg=None):
        self.msg = msg

    def throw(self, error_msg):
        raise Exception(error_msg)

    def validate_json(self, js):
        if not js:
            self.throw('Missing param json_reg')
        try:
            jdec = json.JSONDecoder()
            js = jdec.raw_decode(js)[0]
            js = dict(js)
            return js
        except Exception as e:
            self.throw('Malformed JSON data: %s' %(str(e)))

    def sincronize(self, schema, js):
        try:
            schema = voluptuous.Schema(schema)
            return schema(js)
        except Exception as e:
            self.throw('json_reg data is not according to base definition, details: %s' %str(e))

    def is_integer(self, i):
        try: int(i) ;return True
        except ValueError: return False

    def base_exists(self, base_name):
        if not base_name: self.throw('Missing param "nome_base"!')
        if base_name in get_bases(): return True
        return False

    def xml_to_base(self, xml_base):
        try: return xml_to_base(parseString(xml_base))
        except ExpatError: self.throw('Malformed XML data')

    def split_request(self, request):
        return dict(request.params), request.method

    def filter_params(self, params, valid_fields):
        return { param: params[param] for param in params if param in valid_fields }

    def validate_base_data(self, cls, request):
        params, method = self.split_request(request)
        valid_fields = (
            'id_base',
            'nome_base',
            'xml_base',
            'dt_base'
            )

        data = self.filter_params(params, valid_fields)

        if method == 'POST':
            if not 'nome_base' in data or not 'xml_base' in data:
                self.throw('Required: nome_base, xml_base')
            if self.base_exists(data.get('nome_base')):
                self.throw('Base already exists!')
            data['dt_base'] = str(datetime.datetime.now())
        return data

        if method == 'PUT':
            raise Exception('Not implemented')
            if data.get('dt_base'): del data['dt_base']

    def validate_reg_data(self, cls, request):

        params, method = self.split_request(request)
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

        data = self.filter_params(params, valid_fields)

        if method == 'POST':
            data['dt_reg'] = datetime.datetime.now()
            data['id_reg'] = cls.context._execute(cls.seq)
            json_reg = self.validate_json(data.get('json_reg'))
            json_reg = self.sincronize(cls._base_context()['schema'], json_reg)
            data['json_reg'] = json.dumps(cls.set_id_up(json_reg, data['id_reg']), ensure_ascii=False)
            data.update(cls.get_cc_data(json_reg))

        elif method == 'PUT':

            if 'json_reg' in data:
                json_reg = self.validate_json(data['json_reg'])
                json_reg = self.sincronize(cls._base_context()['schema'], json_reg)

                data['json_reg'] = json.dumps(
                    cls.set_id_up(json_reg, int(request.matchdict['id'])),
                    ensure_ascii=False
                    )

                data.update(cls.get_cc_data(json_reg))
                if not 'dt_index_tex' in data:
                    data['dt_index_tex'] = None

        return data

    def validate_doc_data(self, cls, request):

        params, method = self.split_request(request)
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
                self.throw('Forbidden: More than one document per request')
            return _data

        data = params

        if method == 'POST':
            if not 'id_reg' in params:
                self.throw('Required param: id_reg')
            cls.id_reg = params['id_reg']
            cls.set_json_reg()
            data.update(get_doc(params))

        elif method == 'PUT':
            if has_doc(params):
                if not 'id_reg' in params:
                    self.throw('Trying to insert a new doc? Param "id_reg" is required!')
                else:
                    cls.id_reg = params['id_reg']
                    cls.set_json_reg()
                    data.update(get_doc(params))
            data['dt_ext_texto'] = None
            data['texto_doc'] = None

        return self.filter_params(data, valid_fields)

    def is_sqlinject(self, s):
        s = s.upper()
        sqlinject = (
                    "SELECT",
                    "FROM"
                    "DROP",
                    "INSERT",
                    "DELETE",
                    "UNION",
                    ";",
                    "--",
                    "/*",
                    "XP_",
                    "UTL_",
                    "DBMS_"
                    )
        for statement in sqlinject:
            if statement in s:
                raise Exception('Invalid statements in literal search.')


