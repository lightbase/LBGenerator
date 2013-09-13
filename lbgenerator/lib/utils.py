
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

def sincronize(registry, schema):
    try:
        return schema(registry)
    except Exception as e:
        raise Exception('JSON data is not according to base definition. Details: %s' % str(e))

def is_integer(i):
    try: 
        int(i)
        return True
    except ValueError: 
        return False

def split_request(request):
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
