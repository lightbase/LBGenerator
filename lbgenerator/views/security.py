from functools import wraps
from pyramid.exceptions import Forbidden

from .. import config as global_config
from ..model.context.user import UserContextFactory

INVALID_API_KEY='Invalid API key'


def verify_api_key(view_function):
    ''' Decorator function wich is responsable to 
    check if an api_key in Authentication header 
    is valid.
    '''

    @wraps(view_function)
    def verify(*args, **kwargs):
        request=args[0].request
        if global_config.AUTH_ENABLED is True:
            api_key=extract_token(request)
            if not api_key:
                raise Forbidden(INVALID_API_KEY)

            userContext=UserContextFactory(request)
            user=userContext.get_member_by_api_key(api_key)
            if user is None:
                raise Forbidden(INVALID_API_KEY)
            else:
                return view_function(*args, **kwargs)

        else:
            return view_function(*args, **kwargs)

    return verify

def extract_token(request):
    '''
    Method responsable to extrat an authentication token
    from Authentication header.
    '''

    # TODO: Melhorar forma de obter o token! By Camilo
    try:
        tuple_auth=request.authorization
        if tuple_auth is None or len(tuple_auth) < 2:
            return None
        else:
            header_dict={tuple_auth[0]:tuple_auth[1]}

        if header_dict is not None:
            return header_dict.get('api_key', None)

    except Exception as e :
        return None

    return None
