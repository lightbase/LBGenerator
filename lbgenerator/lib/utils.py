
import json
import datetime
import decimal
from sqlalchemy.util import KeyedTuple as NamedTuple
from liblightbase.lbtypes.extended import FileMask
from liblightbase.lbcodecs import json2object
from liblightbase.lbcodecs import object2json

class FakeRequest(object):

    def __init__(self, params={}, matchdict={}, method='GET'):
        self.params = params
        self.matchdict = matchdict
        self.method = method

class DefaultJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        """Convert ``obj`` to something JSON encoder can handle."""
        datetime_types = (datetime.time, datetime.date, datetime.datetime)
        if isinstance(obj, NamedTuple):
            obj = dict((k, getattr(obj, k)) for k in obj.keys())
        elif isinstance(obj, decimal.Decimal):
            obj = str(obj)
        elif isinstance(obj, datetime.datetime):
            obj = obj.strftime('%d/%m/%Y %H:%M:%S')
        elif isinstance(obj, datetime.time):
            obj = obj.strftime('%H:%M:%S')
        elif isinstance(obj, datetime.date):
            obj = obj.strftime('%d/%m/%Y')
        return obj

def registry2json(registry):
    return object2json(registry, cls=DefaultJSONEncoder)

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
    for param in params:
        if param not in valid_fields:
            raise Exception('Invalid param: %s' % param)
    return dict(params)

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

def is_file_mask(mask):
    try:
        FileMask(**mask)
        return True
    except:
        return False
