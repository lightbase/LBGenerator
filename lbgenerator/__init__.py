from pyramid.config import Configurator
import pyramid_restler
from lbgenerator import model

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    pyramid_restler.includeme(config)
    model.make_restful_app(**settings)

    from lbgenerator.config import routing
    routing.make_routes(config)

    config.scan()

    return config.make_wsgi_app()



