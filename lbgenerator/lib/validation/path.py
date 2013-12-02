
import json
import datetime
from lbgenerator.lib import utils

def validate_path_data(request):

    params, method = utils.split_request(request)
    if method == 'GET':
        return None

    if method == 'POST' and 'return' in params:
        VALID_DATA = [
            'json_reg',
            'json_path',
            'new_path',
            'new_value',
        ]
        if params['return'] not in VALID_DATA:
            raise Exception("""
                param "return" must be one of following: ')
                "json_reg",
                "json_path",
                "new_path",
                "new_value",
            """)

    elif method == 'PUT' and 'return' in params:
        VALID_DATA= [
            'json_reg',
            'new_value'
        ]
        if params['return'] not in VALID_DATA:
            raise Exception("""
                param "return" must be one of following: ')
                "json_reg",
                "new_value"
            """)

    elif method == 'DELETE' and 'return' in params:
        VALID_DATA = [
            'json_reg',
        ]
        if params['return'] not in VALID_DATA:
            raise Exception("""
                param "return" must be one of following: ')
                "json_reg"
            """)

    return params
