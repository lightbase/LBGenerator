from pyramid_restler.model import SQLAlchemyORMContext

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import authenticated_userid
from pyramid.security import Everyone
from pyramid.security import forget
from pyramid.security import remember
from pyramid.view import forbidden_view_config
from pyramid.view import view_config
from pyramid.security import AllPermissionsList

USERS = {}
GROUPS = {}

def groupfinder(userid, request):
    user = USERS.get(userid)
    if user:
        return ['g:%s' % g for g in user.groups]

class RootFactory(SQLAlchemyORMContext):

    __acl__ = [
        (Allow, 'g:admin', AllPermissionsList())
    ]

    def __init__(self, request):
        self.request = request
        #for i in request.params:
        #    print(i, request.params[i])

        #BEARER = request.authorization.get('bearer')

        login = ''
        if 'submit' in request.params:
            login = request.params.get('login', '')
            passwd = request.params.get('passwd', '')

            user = USERS.get(login, None)
            if user and user.check_password(passwd):
                headers = remember(request, login)
            else:
                raise HTTPForbidden()

    def __getitem__(self, key):
        user = USERS[key]
        user.__parent__ = self
        user.__name__ = key
        return user

class User(object):
    @property
    def __acl__(self):
        return [
            (Allow, self.login, 'view'),
        ]

    def __init__(self, login, password, groups=None):
        self.login = login
        self.password = password
        self.groups = groups or []

    def check_password(self, passwd):
        return self.password == passwd

def _make_demo_user(login, **kw):
    kw.setdefault('password', login)
    USERS[login] = User(login, **kw)
    return USERS[login]

_make_demo_user('luser')
_make_demo_user('editor', groups=['editor'])
_make_demo_user('admin', groups=['admin'])








