# -*- coding: utf-8 -*-
from pyramid_restler.view import RESTfulView


def make_routes(config):
    """
    Cria rotas para aplicação do gerador de bases
    """

    # Import token controller and context factory
    from ..views.user import UserView
    from ..model.context.user import UserContextFactory

    # Import Bases controller and context factory
    from ..views.base import BaseCustomView
    from ..model.context.base import BaseContextFactory

    # Import documents controller and context factory
    from ..views.document import DocumentCustomView
    from ..model.context.document import DocumentContextFactory

    # Import files controller and context factory
    from ..views.file import FileCustomView
    from ..model.context.file import FileContextFactory

    # Import filesNull controller and context factory
    from ..views.file_null import FileNullCustonView
    from ..model.context.file_null import FileNullContextFactory

    # Migration views
    from ..views.migration import _import, _export

    # ES Rules
    from ..views.index_error import IndexErrorCustomView
    from ..model.context.index_error import IndexErrorContextFactory

    # Command rules
    from ..views.command import CommandCustomView

    # ES Rules
    from ..views.es import ESCustomView
    from ..model.context.es import ESContextFactory

    # Documentation views
    from ..views.docs import DocsCustomView
    from ..model.context.docs import DocsContextFactory

    # Custom routes
    def add_custom_routes(route_name, pattern, factory_class, view_class, views):
        config.add_route(route_name, pattern, factory=factory_class)
        for view_kw in views:
            config.add_view(view=view_class, route_name=route_name, **view_kw)

    # Import/export routes
    config.add_route('importation', '{base}/_import')
    config.add_view(view=_import, route_name='importation')

    config.add_route('exportation', '{base}/_export')
    config.add_view(view=_export, route_name='exportation')

    # Index error routes
    config.add_restful_routes('_index_error', IndexErrorContextFactory, view=IndexErrorCustomView)
    add_custom_routes('index_error', '_index_error', IndexErrorContextFactory, IndexErrorCustomView, [
        {'attr': 'delete_collection', 'request_method': 'DELETE'},
    ])

    # Command routes
    config.add_route('command', '_command/{command}')
    config.add_view(view=CommandCustomView, route_name='command',
        **{'attr': 'execute', 'request_method': 'POST'}
    )

    # ES routes
    add_custom_routes('elasticsearch', '{base}/es{path:.*}', ESContextFactory, ESCustomView, [
        {'attr': 'get_interface', 'request_method': 'GET'},
        {'attr': 'post_interface', 'request_method': 'POST'},
        {'attr': 'delete_interface', 'request_method': 'DELETE'},

    ])

    config.add_directive('add_restful_base_routes', add_restful_base_routes)
    config.add_static_view('static', 'static', cache_max_age=3600)

    # Documentation routes
    add_custom_routes('api_docs', 'api-docs', DocsContextFactory, DocsCustomView, [
        {'attr': 'api_docs', 'request_method': 'GET', 'renderer': 'json'},
    ])
    add_custom_routes('base_docs', 'api-docs/{x:.*}', DocsContextFactory, DocsCustomView, [
        {'attr': 'api_docs', 'request_method': 'GET', 'renderer': 'json'},
    ])

    #----------------#
    # Authentication # 
    #----------------#

    add_custom_routes('authentication', 'user/login', UserContextFactory, UserView, [
        {'attr': 'authenticate', 'request_method': 'POST'},
    ])
    add_custom_routes('unauthentication', 'user/logout', UserContextFactory, UserView, [
        {'attr': 'unauthenticate', 'request_method': 'POST'},
    ])

    # Restful routes for base users.
    config.add_restful_routes('user', UserContextFactory, view=UserView)

    #-----------------#
    # Document Routes # 
    #-----------------#

    add_custom_routes('full_document', '{base}/doc/{id:\d+}/full', DocumentContextFactory, DocumentCustomView, [
        # Route for full document (with document text)
        {'attr': 'full_document', 'request_method':'GET', 'permission': 'view'}
    ])

    add_custom_routes('path', '{base}/doc/{id:\d+}/{path:.*}', DocumentContextFactory, DocumentCustomView, [
        # Restful routes for document path
        {'attr':'get_path', 'request_method':'GET', 'permission': 'view'},
        {'attr':'set_path', 'request_method':'POST', 'permission': 'create'},
        {'attr':'put_path', 'request_method':'PUT', 'permission': 'edit'},
        {'attr':'delete_path', 'request_method':'DELETE', 'permission': 'delete'}
    ])

    #-----------------#
    # Document Routes # 
    #-----------------#

    config.add_route('text', '{base}/file/{id}/text')

    add_custom_routes('get_doc_column', '{base}/file/{id}/{path:.*}',
        FileContextFactory, FileCustomView, [
        {'attr':'get_path', 'request_method':'GET', 'permission': 'view'},
        {'attr':'create_path', 'request_method':'POST','permission':'create'},
        {'attr':'update_path', 'request_method':'PUT', 'permission': 'edit'},
        {'attr':'delete_path', 'request_method':'DELETE', 'permission': 'delete'}
    ])

    #-----------------#
    # FileNull Routes #
    #-----------------#

    add_custom_routes('get_null_file', '{base}/file/null',
        FileNullContextFactory, FileNullCustonView, [
        {'attr': 'get_file_null', 'request_method': 'Get', 'permission': 'view'}
        ])

    #-------------#
    # Base Routes # 
    #-------------#

    # Restful routes for bases.
    config.add_restful_base_routes()

    # Restful routes for base documents.
    config.add_restful_routes('{base}/doc', DocumentContextFactory, view=DocumentCustomView)

    add_custom_routes('document_collection', '{base}/doc', DocumentContextFactory, DocumentCustomView, [
        # Restful routes for documents collection
        {'attr':'update_collection', 'request_method': 'PUT', 'permission': 'edit'},
        {'attr':'delete_collection', 'request_method': 'DELETE', 'permission': 'delete'}
    ])

    # Restful routes for base files.
    config.add_restful_routes('{base}/file', FileContextFactory, view=FileCustomView)

    add_custom_routes('file_collection', '{base}/file', FileContextFactory, FileCustomView, [
        # Restful routes for files collection
        {'attr':'update_collection', 'request_method': 'PUT', 'permission': 'edit'},
        {'attr':'delete_collection', 'request_method': 'DELETE', 'permission': 'delete'}
    ])

    add_custom_routes('get_base_column', '{base}/{column:.*}', BaseContextFactory, BaseCustomView, [
        # Get specific column route
        {'attr':'get_column', 'request_method':'GET', 'permission': 'view'}
        #{'attr':'set_base_column', 'request_method':'POST', 'permission':'create'},
        #{'attr':'put_base_column', 'request_method':'PUT', 'permission': 'edit'},
        #{'attr':'delete_path', 'request_method':'DELETE', 'permission': 'delete'},
    ])


def add_restful_base_routes(self, name='base'):

    from ..views.base import BaseCustomView
    from ..model.context.base import BaseContextFactory

    view = BaseCustomView
    factory = BaseContextFactory

    route_kw = None
    view_kw = None

    route_kw = {} if route_kw is None else route_kw
    view_kw = {} if view_kw is None else view_kw
    view_kw.setdefault('http_cache', 0)

    subs = dict(
        name=name,
        slug=name.replace('_', '-'),
        base='{base}',
        renderer='{renderer}')

    def add_route(name, pattern, attr, method, **view_kw):
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
        'get_{name}_collection', '/', 'get_collection', 'GET', permission='view')

    # Get member
    add_route(
        'get_{name}_rendered', '/{base}.{renderer}', 'get_member', 'GET', permission='view')
    add_route('get_{name}', '/{base}', 'get_member', 'GET', permission='view')

    # Create member
    add_route('create_{name}', '/', 'create_member', 'POST', permission='create')

    # Update member
    add_route('update_{name}', '/{base}', 'update_member', 'PUT', permission='edit')

    # Delete member
    add_route('delete_{name}', '/{base}', 'delete_member', 'DELETE', permission='delete')


def add_restful_routes(self, name, factory, view=RESTfulView,
                       route_kw=None, view_kw=None):
    """Add a set of RESTful routes for an entity.

    URL patterns for an entity are mapped to a set of views encapsulated in
    a view class. The view class interacts with the model through a context
    adapter that knows the particulars of that model.

    To use this directive in your application, first call
    `config.include('pyramid_restler')` somewhere in your application's
    `main` function, then call `config.add_restful_routes(...)`.

    ``name`` is used as the base name for all route names and patterns. In
    route names, it will be used as-is. In route patterns, underscores will
    be converted to dashes.

    ``factory`` is the model adapter that the view interacts with. It can be
    any class that implements the :class:`pyramid_restler.interfaces.IContext`
    interface.

    ``view`` must be a view class that implements the
    :class:`pyramid_restler.interfaces.IView` interface.

    Additional route and view keyword args can be passed directly through to
    all `add_route` and `add_view` calls. Pass ``route_kw`` and/or ``view_kw``
    as dictionaries to do so.

    """
    route_kw = {} if route_kw is None else route_kw
    view_kw = {} if view_kw is None else view_kw
    view_kw.setdefault('http_cache', 0)

    subs = dict(
        name=name,
        #slug=name.replace('_', '-'),
        slug=name,
        #id='{id:\d+}',
        id='{id}',
        renderer='{renderer}')

    perms = {
        'GET': 'view',
        'POST': 'create',
        'PUT': 'edit',
        'DELETE': 'delete'
    }

    def add_route(name, pattern, attr, method):
        name = name.format(**subs)
        pattern = pattern.format(**subs)
        self.add_route(
            name, pattern, factory=factory,
            request_method=method, **route_kw)
        if name == 'create_user':
            permission = None
        else:
            permission = perms[method]
        self.add_view(
            view=view, attr=attr, route_name=name,
            #request_method=method, **view_kw)
            request_method=method, permission=permission)

    # Get collection
    add_route(
        'get_{name}_collection_rendered', '/{slug}.{renderer}',
        'get_collection', 'GET')

    # Cached routes
    add_route(
        'get_{name}_collection_cached', '/cached/{slug}', 'get_collection_cached', 'GET')

    add_route('get_{name}_cached', '/cached/{slug}/{id}', 'get_member_cached', 'GET')

    # Regular routes
    add_route(
        'get_{name}_collection', '/{slug}', 'get_collection', 'GET')

    # Get member
    add_route(
        'get_{name}_rendered', '/{slug}/{id}.{renderer}', 'get_member', 'GET')
    add_route('get_{name}', '/{slug}/{id}', 'get_member', 'GET')

    # Create member
    add_route('create_{name}', '/{slug}', 'create_member', 'POST')

    # Update member
    add_route('update_{name}', '/{slug}/{id}', 'update_member', 'PUT')

    # Delete member
    add_route('delete_{name}', '/{slug}/{id}', 'delete_member', 'DELETE')
