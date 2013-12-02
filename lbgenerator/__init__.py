from pyramid.config import Configurator
import pyramid_restler
from lbgenerator import model
from lbgenerator.config import set_globals
from lbgenerator.config import routing

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    pyramid_restler.includeme(config)

    set_globals(**settings)

    model.make_restful_app()

    routing.make_routes(config)

    config.scan()

    return config.make_wsgi_app()



