
from liblightbase.lbtypes.extended import FileMask
from liblightbase.lbutils.codecs import *

class FakeRequest(object):

    def __init__(self, params={}, matchdict={}, method='GET'):
        self.params = params
        self.matchdict = matchdict
        self.method = method

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
