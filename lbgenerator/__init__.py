import uuid

import pyramid_restler
from pyramid.settings import asbool
from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from . import model
from .config import routing
from .config import set_globals


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    mem_profiler = asbool(settings.get('mem_profiler', 'False'))
    settings['mem_profiler'] = mem_profiler
    perf_profiler = asbool(settings.get('perf_profiler', 'False'))
    settings['perf_profiler'] = perf_profiler
    config = Configurator(settings=settings)
    config.add_directive('add_restful_routes', routing.add_restful_routes)
    set_globals(**settings)

    from . import config as global_config
    secret = str(uuid.uuid4())

    # NOTE: Beaker include! By John Doe
    config.include('pyramid_beaker')

    # TODO: Talvez faça-se necessário "descomentar" o que vai abaixo!
    # By Questor
    # if global_config.AUTH_ENABLED is True:
        # authn_policy=AuthTktAuthenticationPolicy(
            # secret, 
            # callback=verify_api_key, 
            # hashalg='sha512', 
            # include_ip=global_config.AUTH_INCLUDE_IP
        # )
        # authz_policy=ACLAuthorizationPolicy()
        # config.set_authentication_policy(authn_policy)
        # config.set_authorization_policy(authz_policy)

    model.make_restful_app()
    routing.make_routes(config)
    config.scan()
    app = config.make_wsgi_app()

    # NOTE: Add memory profiler middleware! By John Doe
    if mem_profiler:
        from .mem_profiler import ProfilerMiddleware
        app = ProfilerMiddleware(app)

    if perf_profiler:
        from repoze.profile import ProfileMiddleware
        app = ProfileMiddleware(
            app, 
            log_filename='/var/log/lbg_perf_profile.log', 
            cachegrind_filename='./cachegrind.out.bar', 
            discard_first_request=True, 
            flush_at_shutdown=True, 
            path='/__perf_profiler', 
            unwind=False
        )

    return app

