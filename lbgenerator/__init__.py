from pyramid.config import Configurator
import pyramid_restler
from lbgenerator import model

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from lbgenerator.model.security import groupfinder, RootFactory

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    authn_policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings, root_factory=RootFactory)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    pyramid_restler.includeme(config)
    model.make_restful_app(**settings)

    from lbgenerator.config import routing
    routing.make_routes(config)

    config.scan()

    return config.make_wsgi_app()



