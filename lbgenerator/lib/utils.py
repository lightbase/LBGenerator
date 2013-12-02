
import json

class FakeRequest(object):

    def __init__(self, params={}, matchdict={}, method='GET'):
        self.params = params
        self.matchdict = matchdict
        self.method = method

def to_json(obj):
    if not obj:
        raise Exception('No JSON data supplied.')
    if type(obj) is dict:
        return obj
    if isinstance(obj, str):
        obj = obj.encode('utf-8')
    try:
        obj = json.loads(obj.decode('utf-8'))
        return obj
    except Exception as e:
        raise Exception('Could not parse JSON data. Details: %s' % str(e.args[0]))

def is_integer(i):
    try:
        int(i)
        return True
    except ValueError:
        return False

def split_request(request):
    # TODO: if user send a parameter on get like '%', if not url_encoded, will 
    # raise an utf-8 decode error by webob lib. Need to fix it !!!
    return dict(request.params), request.method

def filter_params(params, valid_fields):
    return { param: params[param] for param in params if param in valid_fields }

def is_sqlinject(s):
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

class FileMask():

    def __init__(self, id_doc, nome_doc, mimetype, uuid):
        self._id_doc = id_doc
        self.nome_doc = nome_doc
        self.mimetype = mimetype
        self.uuid = uuid

    @property
    def _id_doc(self):
        return self.id_doc

    @_id_doc.setter
    def _id_doc(self, id):
        try:
            self.id_doc = int(id)
        except:
            raise Exception('ValueError: id_doc must be integer.')

def is_file_mask(mask):
    try:
        FileMask(**mask)
        return True
    except:
        return False
