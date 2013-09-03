
import json
import traceback

def to_json(string):
    try:
        string.encode('utf-8')
        return json.loads(string)
    except Exception as e:
        raise Exception('Malformed JSON data. Details: %s' % str(e))

def sincronize(js, schema):
    try:
        return schema(js)
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
