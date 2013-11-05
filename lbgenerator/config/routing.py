# -*- coding: utf-8 -*-
from lbgenerator.model.context.base import BaseContextFactory
from lbgenerator.model.context.registry import RegContextFactory
from lbgenerator.model.context.document import DocContextFactory
from lbgenerator.views.base import BaseCustomView
from lbgenerator.views.registry import RegCustomView
from lbgenerator.views.document import DocCustomView


def make_routes(config):
    """
    Cria rotas para aplicação do gerador de bases
    """

    config.add_directive('add_restful_base_routes', add_restful_base_routes)
    config.add_static_view('static', 'static', cache_max_age=3600)

    # Restful routes for bases.
    config.add_restful_base_routes()

    # Restful routes for base registries.
    config.add_restful_routes('{base}/reg', RegContextFactory, view=RegCustomView)

    # Restful routes for base files.
    config.add_restful_routes('{base}/doc', DocContextFactory, view=DocCustomView)

    # File Download View
    config.add_route('download', '{base}/doc/{id}/download', factory=DocContextFactory)
    config.add_view(view=DocCustomView, attr='download', route_name='download', request_method='GET')

    # Restful routes for registry path
    config.add_route('path', '{base}/reg/{id}/path/{path}', factory=RegContextFactory)
    config.add_view(view=RegCustomView, attr='get_path', route_name='path', request_method='GET')
    config.add_view(view=RegCustomView, attr='set_path', route_name='path', request_method='POST')
    config.add_view(view=RegCustomView, attr='put_path', route_name='path', request_method='PUT')
    config.add_view(view=RegCustomView, attr='delete_path', route_name='path', request_method='DELETE')

    config.add_route('text', '{base}/doc/{id}/text')

    # Restful route for full registry (with document text)
    config.add_route('full_reg', '{base}/reg/{id}/full', factory=RegContextFactory)
    config.add_view(view=RegCustomView, attr='full_reg', route_name='full_reg', request_method='GET')

    # Route for putting text on file
    #config.add_route('doc_text', '{base}/doc/{id}/text', factory=DocContextFactory)
    #config.add_view(view=DocCustomView, attr='text', route_name='doc_text', request_method='PUT')

def add_restful_base_routes(self, name='base', factory=BaseContextFactory, view=BaseCustomView):
    route_kw=None
    view_kw=None

    route_kw = {} if route_kw is None else route_kw
    view_kw = {} if view_kw is None else view_kw
    view_kw.setdefault('http_cache', 0)

    subs = dict(
        name=name,
        slug=name.replace('_', '-'),
        id='{id}',
        renderer='{renderer}')

    def add_route(name, pattern, attr, method):
        name = name.format(**subs)
        pattern = pattern.format(**subs)
        self.add_route(
            name, pattern, factory=factory,
            request_method=method, **route_kw)
        self.add_view(
            view=view, attr=attr, route_name=name,
            request_method=method, **view_kw)

    # Get collection
    add_route(
        'get_{name}_collection', '/', 'get_collection', 'GET')

    # Get member
    add_route(
        'get_{name}_rendered', '/{id}.{renderer}', 'get_member', 'GET')
    add_route('get_{name}', '/{id}', 'get_member', 'GET')

    # Create member
    add_route('create_{name}', '/', 'create_member', 'POST')

    # Update member
    add_route('update_{name}', '/{id}', 'update_member', 'PUT')

    # Delete member
    add_route('delete_{name}', '/{id}', 'delete_member', 'DELETE')



