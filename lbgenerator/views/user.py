
from . import CustomView
from ..lib.validation.user import validate_user_data
from ..lib.exceptions import OAuth2ErrorHandler
from .. import config
from pyramid.security import authenticated_userid
from pyramid.security import remember
from pyramid.security import forget
from pyramid.response import Response
from pyramid.httpexceptions import HTTPOk, HTTPForbidden
from pyramid.exceptions import HTTPNotFound

class UserView(CustomView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _get_data(self):
        return validate_user_data(self, self.request)

    def create_member(self):
        data = self._get_data()
        same_user = self.context.get_member(data['nm_user'])
        if same_user:
            raise Exception("user '%s' already exists!" % data['nm_user'])
        member = self.context.create_member(data)
        id = self.context.get_member_id_as_string(member)
        return self.render_custom_response(id, default_response=id)

    def authenticate(self):
        """
        The token endpoint is used by the client to obtain an access token by
        presenting its authorization grant or refresh token. The token
        endpoint is used with every authorization grant except for the
        implicit grant type (since an access token is issued directly).
        """
        user = self.request.params.get('nm_user')
        passwd = self.request.params.get('passwd_user')

        if user is None:
            raise Exception('Required parameter nm_user not found in the request')
        elif passwd is None:
            raise Exception("Required parameter 'passwd_user' not found in the request")

        if user == config.ADMIN_USER and passwd == config.ADMIN_PASSWD:
            headers = remember(self.request, user)
            return Response('OK', headers=headers)

        member = self.context.get_member(user)
        if not member:
            raise Exception('No such User!')

        if member.passwd_user != passwd:
            raise Exception('Invalid Password!')

        headers = remember(self.request, user)
        return Response('OK', headers=headers)

    def test_login(self):
        logged_in = authenticated_userid(self.request)
        return Response(str(logged_in))
        
    def unauthenticate(self):
        headers = forget(self.request)
        return Response('OK', headers=headers)



