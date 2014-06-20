from . import model
from .config import set_globals
from .config import routing
from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig
import pyramid_restler
import uuid

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.add_directive('add_restful_routes', routing.add_restful_routes)
    set_globals(**settings)

    from . import config as global_config

    secret =  str(uuid.uuid4())

    if global_config.AUTH_ENABLED is True:

        authn_policy = AuthTktAuthenticationPolicy(secret,
            callback=model.user_callback, hashalg='sha512', include_ip=global_config.AUTH_INCLUDE_IP)
        authz_policy = ACLAuthorizationPolicy()

        config.set_authentication_policy(authn_policy)
        config.set_authorization_policy(authz_policy)

    model.make_restful_app()
    routing.make_routes(config)
    config.scan()

    return config.make_wsgi_app()
