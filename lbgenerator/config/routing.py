# -*- coding: utf-8 -*-
from pyramid_restler.view import RESTfulView


# self <- <pyramid.self.Configurator object>
def make_routes(self):
    """ Cria rotas para aplicação do gerador de bases
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

    # Migration views
    from ..views.migration import _import, _export

    # ES Rules
    from ..views.index_error import IndexErrorCustomView
    from ..model.context.index_error import IndexErrorContextFactory

    # Regras p/ gerenciamento da indexação textual (índices)
    from ..views.txt_idx import TxtIdxCustomView
    from ..model.context.txt_idx import TxtIdxContextFactory

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
        self.add_route(route_name, pattern, factory=factory_class)
        for view_kw in views:
            self.add_view(view=view_class, route_name=route_name, **view_kw)

    # Import/export routes
    # * "GET" (?)
    # - Ação: (?)
    # - Rota: "{base}/_import"
    # - Parâmetros: URI (?)
    self.add_route('importation', '{base}/_import')
    self.add_view(view=_import, route_name='importation')

    # * "GET" (?)
    # - Ação: (?)
    # - Rota: "{base}/_export"
    # - Parâmetros: URI (?)
    self.add_route('exportation', '{base}/_export')
    self.add_view(view=_export, route_name='exportation')

    # * "GET" (?)
    # - Ação: (?)
    # - Rota: "_txt_idx"
    # - Parâmetros: URI (?)
    # self.add_restful_routes('_txt_idx', TxtIdxContextFactory, view=TxtIdxCustomView)

    # _txt_idx routes
    add_custom_routes(
        '_txt_idx_get_put_delete', '_txt_idx/{nm_idx}', 
        TxtIdxContextFactory, TxtIdxCustomView, 
        [
            {
                'attr':'get_member', 'request_method':'GET', 
                'permission': 'view'
            }, 
            {
                'attr':'update_member', 'request_method':'PUT', 
                'permission': 'edit'
            }, 
            {
                'attr':'delete_member', 'request_method':'DELETE', 
                'permission': 'delete'
            } 
        ])

    add_custom_routes(
        '_txt_idx_post', '_txt_idx', 
        TxtIdxContextFactory, TxtIdxCustomView, 
        [
            {
                'attr':'create_member', 'request_method':'POST', 
                'permission': 'create'
            }
        ])

    # Index error routes
    # * "GET" (?)
    # - Ação: (?)
    # - Rota: "_index_error"
    # - Parâmetros: URI (?)
    self.add_restful_routes('_index_error', IndexErrorContextFactory, view=IndexErrorCustomView)

    add_custom_routes('index_error', '_index_error', IndexErrorContextFactory, IndexErrorCustomView, [
        # * "DELETE"
        # - Ação: (?)
        # - Rota: "_index_error"
        # - Parâmetros: URI, form
        {'attr': 'delete_collection', 'request_method': 'DELETE'},
    ])

    # Command routes
    # * "GET" (?)
    # - Ação: (?)
    # - Rota: "_command/{command}"
    # - Parâmetros: URI (?)
    self.add_route('command', '_command/{command}')

    self.add_view(view=CommandCustomView, route_name='command',
        # * "POST"
        # - Ação: (?)
        # - Rota: "_command/{command}"
        # - Parâmetros: URI, form
        **{'attr': 'execute', 'request_method': 'POST'}
    )

    # ES routes
    add_custom_routes('elasticsearch', '{base}/es{path:.*}', ESContextFactory, ESCustomView, [
        # * "GET"
        # - Ação: (?)
        # - Rota: "{base}/es{path:.*}"
        # - Parâmetros: URI
        {'attr': 'get_interface', 'request_method': 'GET'},
        # * "POST"
        # - Ação: (?)
        # - Rota: "{base}/es{path:.*}"
        # - Parâmetros: URI, form
        {'attr': 'post_interface', 'request_method': 'POST'},
        # * "DELETE"
        # - Ação: (?)
        # - Rota: "{base}/es{path:.*}"
        # - Parâmetros: URI, form
        {'attr': 'delete_interface', 'request_method': 'DELETE'}
    ])

    # ES routes (lbes - simplified)
    from ..views.lbes import LBSearch
    self.add_route('lbes', '{base}/lbes{path:.*}', request_method='POST')
    self.add_view(view=LBSearch, route_name='lbes', request_method='POST',
        header='Content-Type:application/json', renderer='json')

    self.add_directive('add_restful_base_routes', add_restful_base_routes)
    self.add_static_view('static', 'static', cache_max_age=3600)

    # Documentation routes
    add_custom_routes('api_docs', 'api-docs', DocsContextFactory, DocsCustomView, [
        # * "GET"
        # - Ação: (?)
        # - Rota: "api-docs"
        # - Parâmetros: URI
        {'attr': 'api_docs', 'request_method': 'GET', 'renderer': 'json'},
    ])
    add_custom_routes('base_docs', 'api-docs/{x:.*}', DocsContextFactory, DocsCustomView, [
        # * "GET"
        # - Ação: (?)
        # - Rota: "api-docs/{x:.*}"
        # - Parâmetros: URI
        {'attr': 'api_docs', 'request_method': 'GET', 'renderer': 'json'},
    ])

    #----------------#
    # Authentication # 
    #----------------#

    add_custom_routes('authentication', 'user/login', UserContextFactory, UserView, [
        # * "POST"
        # - Ação: (?)
        # - Rota: "user/login"
        # - Parâmetros: URI, form
        {'attr': 'authenticate', 'request_method': 'POST'},
    ])
    add_custom_routes('unauthentication', 'user/logout', UserContextFactory, UserView, [
        # * "POST"
        # - Ação: (?)
        # - Rota: "user/logout"
        # - Parâmetros: URI, form
        {'attr': 'unauthenticate', 'request_method': 'POST'},
    ])

    # * "GET" (?)
    # - Ação: (?)
    # - Rota: "user"
    # - Parâmetros: URI (?)
    self.add_restful_routes('user', UserContextFactory, view=UserView)

    #-----------------#
    # Document Routes # 
    #-----------------#

    # Route for full document (with document text)
    add_custom_routes('full_document', '{base}/doc/{id:\d+}/full', DocumentContextFactory, DocumentCustomView, [
        # * "GET"
        # - Ação: (?)
        # - Rota: "{base}/doc/{id:\d+}/full"
        # - Parâmetros: URI
        {'attr': 'full_document', 'request_method':'GET', 'permission': 'view'}
    ])

    # Restful routes for document path
    add_custom_routes('path', '{base}/doc/{id:\d+}/{path:.*}', DocumentContextFactory, DocumentCustomView, [
        # * "GET"
        # - Ação: (?)
        # - Rota: "{base}/doc/{id:\d+}/{path:.*}"
        # - Parâmetros: URI
        {'attr':'get_path', 'request_method':'GET', 'permission': 'view'},
        # * "POST"
        # - Ação: (?)
        # - Rota: "{base}/doc/{id:\d+}/{path:.*}"
        # - Parâmetros: URI, form
        {'attr':'set_path', 'request_method':'POST', 'permission': 'create'},
        # * "PUT"
        # - Ação: (?)
        # - Rota: "{base}/doc/{id:\d+}/{path:.*}"
        # - Parâmetros: URI, form
        {'attr':'put_path', 'request_method':'PUT', 'permission': 'edit'},
        # * "DELETE"
        # - Ação: (?)
        # - Rota: "{base}/doc/{id:\d+}/{path:.*}"
        # - Parâmetros: URI, form
        {'attr':'delete_path', 'request_method':'DELETE', 'permission': 'delete'}
    ])

    #-----------------#
    # Document Routes # 
    #-----------------#

    # Obter texto do registro do "tipo file".
    # * "GET" (?)
    # - Ação: (?)
    # - Rota: "{base}/file/{id}/text"
    # - Parâmetros: URI (?)
    self.add_route('text', '{base}/file/{id}/text')

    # Obter itens de grupos (monovalorados/multivalorados) de registro
    # do "tipo doc".
    add_custom_routes('get_doc_column', '{base}/file/{id}/{path:.*}',
        FileContextFactory, FileCustomView, [
        # * "GET"
        # - Ação: (?)
        # - Rota: "{base}/file/{id}/{path:.*}"
        # - Parâmetros: URI
        {'attr':'get_path', 'request_method':'GET', 'permission': 'view'},
        # * "POST"
        # - Ação: (?)
        # - Rota: "{base}/file/{id}/{path:.*}"
        # - Parâmetros: URI, form
        {'attr':'create_path', 'request_method':'POST','permission':'create'},
        # * "PUT"
        # - Ação: (?)
        # - Rota: "{base}/file/{id}/{path:.*}"
        # - Parâmetros: URI, form
        {'attr':'update_path', 'request_method':'PUT', 'permission': 'edit'},
        # * "DELETE"
        # - Ação: (?)
        # - Rota: "{base}/file/{id}/{path:.*}"
        # - Parâmetros: URI, form
        {'attr':'delete_path', 'request_method':'DELETE', 'permission': 'delete'}
    ])

    #-------------#
    # Base Routes # 
    #-------------#

    # Restful routes for bases.
    self.add_restful_base_routes()

    # Restful routes for base documents.
    # * "GET" (?)
    # - Ação: (?)
    # - Rota: "{base}/doc"
    # - Parâmetros: URI (?)
    self.add_restful_routes('{base}/doc', DocumentContextFactory, view=DocumentCustomView)

    # PATCH route for documents
    add_custom_routes('patch_doc', '{base}/doc/{id}', DocumentContextFactory, DocumentCustomView, [
        # * "PATCH"
        # - Ação: (?)
        # - Rota: "{base}/doc"
        # - Parâmetros: form
        {'attr': 'patch_member', 'request_method': 'PATCH', 'permission': 'patch'}
    ])

    # Restful routes for documents collection
    add_custom_routes('document_collection', '{base}/doc', DocumentContextFactory, DocumentCustomView, [
        # * "PUT"
        # - Ação: (?)
        # - Rota: "{base}/doc"
        # - Parâmetros: form
        {'attr':'update_collection', 'request_method': 'PUT', 'permission': 'edit'},
        # * "DELETE"
        # - Ação: (?)
        # - Rota: "{base}/doc"
        # - Parâmetros: form
        {'attr':'delete_collection', 'request_method': 'DELETE', 'permission': 'delete'}
    ])

    # Restful routes for base files.
    # * "GET" (?)
    # - Ação: (?)
    # - Rota: "{base}/file"
    # - Parâmetros: URI (?)
    self.add_restful_routes('{base}/file', FileContextFactory, view=FileCustomView)

    # Restful routes for files collection.
    add_custom_routes('file_collection', '{base}/file', FileContextFactory, FileCustomView, [
        # * "PUT"
        # - Ação: (?)
        # - Rota: "{base}/file"
        # - Parâmetros: form
        {'attr':'update_collection', 'request_method': 'PUT', 'permission': 'edit'},
        # * "DELETE"
        # - Ação: (?)
        # - Rota: "{base}/file"
        # - Parâmetros: form
        {'attr':'delete_collection', 'request_method': 'DELETE', 'permission': 'delete'}
    ])

    # Get specific column route.
    add_custom_routes('get_base_column', '{base}/{column:.*}', BaseContextFactory, BaseCustomView, [
        # * "GET"
        # - Ação: (?)
        # - Rota: "{base}/{column:.*}"
        # - Parâmetros: URI
        {'attr':'get_column', 'request_method':'GET', 'permission': 'view'}
        #{'attr':'set_base_column', 'request_method':'POST', 'permission':'create'},
        #{'attr':'put_base_column', 'request_method':'PUT', 'permission': 'edit'},
        #{'attr':'delete_path', 'request_method':'DELETE', 'permission': 'delete'},
    ])


# self <- <pyramid.self.Configurator object>
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
    # * "GET"
    # - Ação: (?)
    # - Rota: "/"
    # - Parâmetros: URI
    add_route(
        'get_{name}_collection', '/', 'get_collection', 'GET', permission='view')

    # Get member
    # * "GET"
    # - Ação: (?)
    # - Rota: "/{base}.{renderer}"
    # - Parâmetros: URI
    add_route(
        'get_{name}_rendered', '/{base}.{renderer}', 'get_member', 'GET', permission='view')

    # * "GET"
    # - Ação: (?)
    # - Rota: "/{base}"
    # - Parâmetros: URI
    add_route('get_{name}', '/{base}', 'get_member', 'GET', permission='view')

    # Create member
    # * "POST"
    # - Ação: (?)
    # - Rota: "/"
    # - Parâmetros: URI, form
    add_route('create_{name}', '/', 'create_member', 'POST', permission='create')

    # Update member
    # * "PUT"
    # - Ação: (?)
    # - Rota: "/{base}"
    # - Parâmetros: URI, form
    add_route('update_{name}', '/{base}', 'update_member', 'PUT', permission='edit')

    # Delete member
    # * "DELETE"
    # - Ação: (?)
    # - Rota: "/{base}"
    # - Parâmetros: URI, form
    add_route('delete_{name}', '/{base}', 'delete_member', 'DELETE', permission='delete')

    # LBRAD routes
    from ..views.lbrad import dispatch_msg
    self.add_route('lbrad', '/lbrad', request_method='POST')
    self.add_view(view=dispatch_msg, route_name='lbrad', request_method='POST', renderer='json')
    
    from ..views.lbrad import dispatch_msg_multipart
    self.add_view(view=dispatch_msg_multipart, route_name='lbrad', 
        request_method='POST', header='Content-Type:multipart/form-data', renderer='json')

    # SQL commands routes
    from ..views.sql import execute_sql
    from ..model.context import CustomContextFactory
    self.add_route('sql', '/sql', request_method='POST')
    self.add_view(view=execute_sql, route_name='sql', request_method='POST', 
        header='Content-Type:application/json', renderer='json')

# Esse método faz chamadas p/ o método "add_route()". O objetivo é
# permitir adicionar rotas de forma dinâmica! Também serve para
# "concentrar" a criação de várias rotas de forma simples!
# self <- <pyramid.config.Configurator object>
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
    as dictionaries to do so."""

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
    # * "GET"
    # - Ação: (?)
    # - Rota: "/{slug}.{renderer}"
    # - Parâmetros: URI
    add_route(
        'get_{name}_collection_rendered', '/{slug}.{renderer}',
        'get_collection', 'GET')

    # Cached routes
    # * "GET"
    # - Ação: (?)
    # - Rota: "/cached/{slug}"
    # - Parâmetros: URI
    add_route(
        'get_{name}_collection_cached', '/cached/{slug}', 'get_collection_cached', 'GET')

    # * "GET"
    # - Ação: (?)
    # - Rota: "/cached/{slug}/{id}"
    # - Parâmetros: URI
    add_route('get_{name}_cached', '/cached/{slug}/{id}', 'get_member_cached', 'GET')

    # Regular routes
    # * "GET"
    # - Ação: (?)
    # - Rota: "/{slug}"
    # - Parâmetros: URI
    add_route(
        'get_{name}_collection', '/{slug}', 'get_collection', 'GET')

    # Get member
    # * "GET"
    # - Ação: (?)
    # - Rota: "/{slug}/{id}.{renderer}"
    # - Parâmetros: URI
    add_route(
        'get_{name}_rendered', '/{slug}/{id}.{renderer}', 'get_member', 'GET')

    # * "GET"
    # - Ação: (?)
    # - Rota: "/{slug}/{id}"
    # - Parâmetros: URI
    add_route('get_{name}', '/{slug}/{id}', 'get_member', 'GET')

    # Create member
    # * "POST"
    # - Ação: (?)
    # - Rota: "/{slug}"
    # - Parâmetros: URI, form
    add_route('create_{name}', '/{slug}', 'create_member', 'POST')

    # Update member
    # * "PUT"
    # - Ação: (?)
    # - Rota: "/{slug}/{id}"
    # - Parâmetros: URI, form
    add_route('update_{name}', '/{slug}/{id}', 'update_member', 'PUT')

    # {slug} e {name} recebem o que vai no parâmetro "name" da chamada
    # do método! Ex.: Se name recebe "{base}/doc"...
    # str(name) -> delete_{name}
    # str(pattern) -> /{slug}/{id}
    # str(name.format(**subs)) -> delete_{base}/doc
    # str(pattern.format(**subs)) -> /{base}/doc/{id}

    # Delete member
    # * "DELETE"
    # - Ação: Deletar um item usando passando a sua ID!
    # - Rota: "/{slug}/{id}"
    # - Parâmetros: URI, form
    add_route('delete_{name}', '/{slug}/{id}', 'delete_member', 'DELETE')

