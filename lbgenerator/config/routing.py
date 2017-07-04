from pyramid_restler.view import RESTfulView


def make_routes(self):
    """ Cria rotas para aplicação do gerador de bases
    """

    # NOTE: Import token controller and context factory! By John Doe
    from ..views.user import UserView
    from ..model.context.user import UserContextFactory

    # NOTE: Import Bases controller and context factory! By John Doe
    from ..views.base import BaseCustomView
    from ..model.context.base import BaseContextFactory

    # NOTE: Import documents controller and context factory! By John Doe
    from ..views.document import DocumentCustomView
    from ..model.context.document import DocumentContextFactory

    # NOTE: Import files controller and context factory! By John Doe
    from ..views.file import FileCustomView
    from ..model.context.file import FileContextFactory

    # NOTE: Migration views! By John Doe
    from ..views.migration import _import, _export

    # NOTE: ES Rules! By John Doe
    from ..views.index_error import IndexErrorCustomView
    from ..model.context.index_error import IndexErrorContextFactory

    # NOTE: Regras p/ gerenciamento da indexação textual (índices)! By John Doe
    from ..views.txt_idx import TxtIdxCustomView
    from ..model.context.txt_idx import TxtIdxContextFactory

    # NOTE: Command rules! By John Doe
    from ..views.command import CommandCustomView

    # NOTE: ES Rules! By John Doe
    from ..views.es import ESCustomView
    from ..model.context.es import ESContextFactory

    # NOTE: Documentation views! By John Doe
    from ..views.docs import DocsCustomView
    from ..model.context.docs import DocsContextFactory

    # NOTE: Custom routes! By John Doe
    def add_custom_routes(
            route_name, 
            pattern, 
            factory_class, 
            view_class, 
            views
        ):
        self.add_route(route_name, pattern, factory=factory_class)
        for view_kw in views:
            self.add_view(view=view_class, route_name=route_name, **view_kw)

    # NOTE: Import/export routes! By John Doe
    self.add_route('importation', '{base}/_import')
    self.add_view(view=_import, route_name='importation')
    self.add_route('exportation', '{base}/_export')
    self.add_view(view=_export, route_name='exportation')

    # NOTE: _txt_idx routes! By John Doe
    add_custom_routes(
        '_txt_idx_get_put_delete', 
        '_txt_idx/{nm_idx}', 
        TxtIdxContextFactory, 
        TxtIdxCustomView, 
        [
            {
                'attr': 'get_member', 
                'request_method': 'GET', 
                'permission': 'view'
            }, 
            {
                'attr': 'update_member', 
                'request_method': 'PUT', 
                'permission': 'edit'
            }, 
            {
                'attr': 'delete_member', 
                'request_method': 'DELETE', 
                'permission': 'delete'
            }
        ]
    )

    add_custom_routes(
        '_txt_idx_post', 
        '_txt_idx', 
        TxtIdxContextFactory, 
        TxtIdxCustomView, 
        [
            {
                'attr':'create_member', 
                'request_method':'POST', 
                'permission': 'create'
            }
        ]
    )

    # NOTE: Index error routes! By John Doe
    self.add_restful_routes(
        '_index_error', 
        IndexErrorContextFactory, 
        view=IndexErrorCustomView
    )

    add_custom_routes(
        'index_error', 
        '_index_error', 
        IndexErrorContextFactory, 
        IndexErrorCustomView, 
        [
            {
                'attr': 'delete_collection', 
                'request_method': 'DELETE'
            }
        ]
    )

    # NOTE: Command routes! By John Doe
    self.add_route('command', '_command/{command}')

    self.add_view(
        view=CommandCustomView, 
        route_name='command', 
        **{
            'attr': 'execute', 
            'request_method': 'POST'
        }
    )

    # NOTE: ES routes! By John Doe
    add_custom_routes(
        'elasticsearch', 
        '{base}/es{path:.*}', 
        ESContextFactory, 
        ESCustomView, 
        [
            {
                'attr': 'get_interface', 
                'request_method': 'GET'
            }, 
            {
                'attr': 'post_interface', 
                'request_method': 'POST'
            }, 
            {
                'attr': 'delete_interface', 
                'request_method': 'DELETE'
            }
        ]
    )

    # NOTE: ES routes (lbes - simplified)! By John Doe
    from ..views.lbes import LBSearch

    self.add_route(
        'lbes', 
        '{base}/lbes{path:.*}', 
        request_method='POST'
    )
    self.add_view(
        view=LBSearch, 
        route_name='lbes', 
        request_method='POST', 
        header='Content-Type:application/json', 
        renderer='json'
    )
    self.add_directive('add_restful_base_routes', add_restful_base_routes)
    self.add_static_view('static', 'static', cache_max_age=3600)

    # NOTE: Documentation routes! By John Doe
    add_custom_routes(
        'api_docs', 
        'api-docs', 
        DocsContextFactory, 
        DocsCustomView, 
        [
            {
                'attr': 'api_docs', 
                'request_method': 'GET', 
                'renderer': 'json'
            }
        ]
    )

    add_custom_routes(
        'base_docs', 
        'api-docs/{x:.*}', 
        DocsContextFactory, 
        DocsCustomView, 
        [
            {
                'attr': 'api_docs', 
                'request_method': 'GET', 
                'renderer': 'json'
            }
        ]
    )

    # NOTE: Authentication! By John Doe

    add_custom_routes(
        'authentication', 
        'user/login', 
        UserContextFactory, 
        UserView, 
        [
            {
                'attr': 'authenticate', 
                'request_method': 'POST'
            }
        ]
    )
    add_custom_routes(
        'unauthentication', 
        'user/logout', 
        UserContextFactory, 
        UserView, 
        [
            {
                'attr': 'unauthenticate', 
                'request_method': 'POST'
            }
        ]
    )
    self.add_restful_routes('user', UserContextFactory, view=UserView)

    # NOTE: Document Routes! John Doe

    # NOTE: Route for full document (with document text)! John Doe
    add_custom_routes(
        'full_document', 
        '{base}/doc/{id:\d+}/full', 
        DocumentContextFactory, 
        DocumentCustomView, 
        [
            {
                'attr': 'full_document', 
                'request_method': 'GET', 
                'permission': 'view'
            }
        ]
    )

    # NOTE: Restful routes for document path! By John Doe
    add_custom_routes(
        'path', 
        '{base}/doc/{id:\d+}/{path:.*}', 
        DocumentContextFactory, 
        DocumentCustomView, 
        [
            {
                'attr': 'get_path', 
                'request_method': 'GET', 
                'permission': 'view'
            }, 
            {
                'attr': 'set_path', 
                'request_method': 'POST', 
                'permission': 'create'
            }, 
            {
                'attr': 'put_path', 
                'request_method': 'PUT', 
                'permission': 'edit'
            }, 
            {
                'attr': 'patch_path', 
                'request_method': 'PATCH', 
                'permission': 'edit'
            }, 
            {
                'attr': 'delete_path', 
                'request_method': 'DELETE', 
                'permission': 'delete'
            }
        ]
    )

    # NOTE: Document Routes! By John Doe

    # NOTE: Obter texto do registro do "tipo file"! By John Doe
    self.add_route('text', '{base}/file/{id}/text')

    # NOTE: Obter itens de grupos (monovalorados/multivalorados) de registro
    # do "tipo doc"! By John Doe
    add_custom_routes(
        'get_doc_column', 
        '{base}/file/{id}/{path:.*}', 
        FileContextFactory, 
        FileCustomView, 
        [
            {
                'attr': 'get_path', 
                'request_method': 'GET', 
                'permission': 'view'
            }, 
            {
                'attr': 'create_path', 
                'request_method': 'POST', 
                'permission': 'create'
            }, 
            {
                'attr': 'update_path', 
                'request_method': 'PUT', 
                'permission': 'edit'
            }, 
            {
                'attr': 'delete_path', 
                'request_method': 'DELETE', 
                'permission': 'delete'
            }
        ]
    )

    # NOTE: Base Routes! By John Doe

    # NOTE: Restful routes for bases! By John Doe
    self.add_restful_base_routes()

    # NOTE: Restful routes for base documents! By John Doe
    self.add_restful_routes(
        '{base}/doc', 
        DocumentContextFactory, 
        view=DocumentCustomView
    )

    # NOTE: PATCH route for documents! By John Doe
    add_custom_routes(
        'patch_doc', 
        '{base}/doc/{id}', 
        DocumentContextFactory, 
        DocumentCustomView, 
        [
            {
                'attr': 'patch_member', 
                'request_method': 'PATCH', 
                'permission': 'edit'
            }
        ]
    )

    # NOTE: Restful routes for documents collection! By John Doe
    add_custom_routes(
        'document_collection', 
        '{base}/doc', 
        DocumentContextFactory, 
        DocumentCustomView, 
        [
            {
                'attr': 'update_collection', 
                'request_method': 'PUT', 
                'permission': 'edit'
            }, 
            {
                'attr': 'patch_collection', 
                'request_method': 'PATCH', 
                'permission': 'edit'
            }, 
            {
                'attr': 'delete_collection', 
                'request_method': 'DELETE', 
                'permission': 'delete'
            }
        ]
    )

    # NOTE: Restful routes for base files! By John Doe
    self.add_restful_routes(
        '{base}/file', 
        FileContextFactory, 
        view=FileCustomView
    )

    # NOTE: Restful routes for files collection! By John Doe
    add_custom_routes(
        'file_collection', 
        '{base}/file', 
        FileContextFactory, 
        FileCustomView, 
        [
            {
                'attr': 'update_collection', 
                'request_method': 'PUT', 
                'permission': 'edit'
            }, 
            {
                'attr': 'delete_collection', 
                'request_method': 'DELETE', 
                'permission': 'delete'
            }
        ]
    )

    # NOTE: Get specific column route! By John Doe
    add_custom_routes(
        'get_base_column', 
        '{base}/{column:.*}', 
        BaseContextFactory, 
        BaseCustomView, 
        [
            {
                'attr': 'get_column', 
                'request_method': 'GET', 
                'permission': 'view'
            }, 
            {
                'attr': 'put_column', 
                'request_method': 'PUT', 
                'permission': 'edit'
            }
        ]
    )

    # NOTE: RAD routes! By John Doe

    from ..views.lbrad import dispatch_msg

    self.add_route('lbrad', '/lbrad', request_method='POST')
    self.add_view(
        view=dispatch_msg, 
        route_name='lbrad', 
        request_method='POST', 
        renderer='json'
    )

    from ..views.lbrad import dispatch_msg_multipart

    self.add_view(
        view=dispatch_msg_multipart, 
        route_name='lbrad', 
        request_method='POST', 
        header='Content-Type:multipart/form-data', 
        renderer='json'
    )

    # NOTE: SQL routes! By John Doe

    from ..views.sql import execute_sql
    from ..model.context import CustomContextFactory

    self.add_route('sql', '/sql', request_method='POST')
    self.add_view(
        view=execute_sql, 
        route_name='sql', 
        request_method='POST', 
        header='Content-Type:application/json', 
        renderer='json'
    )

def add_restful_base_routes(self, name='base'):

    from ..views.base import BaseCustomView
    from ..model.context.base import BaseContextFactory

    view=BaseCustomView
    factory=BaseContextFactory
    route_kw=None
    view_kw=None
    route_kw={} if route_kw is None else route_kw
    view_kw={} if view_kw is None else view_kw
    view_kw.setdefault('http_cache', 0)
    subs=dict(
        name=name, 
        slug=name.replace('_', '-'), 
        base='{base}', 
        renderer='{renderer}'
    )

    def add_route(name, pattern, attr, method, **view_kw):
        name=name.format(**subs)
        pattern=pattern.format(**subs)
        self.add_route(
            name, 
            pattern, 
            factory=factory, 
            request_method=method, 
            **route_kw
        )
        self.add_view(
            view=view, 
            attr=attr, 
            route_name=name, 
            request_method=method, 
            **view_kw
        )

    # NOTE: Get collection! By John Doe
    add_route(
        'get_{name}_collection', 
        '/', 
        'get_collection', 
        'GET', 
        permission='view'
    )

    # NOTE: Get member! By John Doe
    add_route(
        'get_{name}_rendered', 
        '/{base}.{renderer}', 
        'get_member', 
        'GET', 
        permission='view'
    )

    add_route(
        'get_{name}', 
        '/{base}', 
        'get_member', 
        'GET', 
        permission='view'
    )

    # NOTE: Create member! By John Doe
    add_route(
        'create_{name}', 
        '/', 
        'create_member', 
        'POST', 
        permission='create'
    )

    # NOTE: Update member! By John Doe
    add_route(
        'update_{name}', 
        '/{base}', 
        'update_member', 
        'PUT', 
        permission='edit'
    )

    # NOTE: Delete member! By John Doe
    add_route(
        'delete_{name}', 
        '/{base}', 
        'delete_member', 
        'DELETE', 
        permission='delete'
    )

# NOTE: Esse método faz chamadas p/ o método "add_route()". O objetivo é
# permitir adicionar rotas de forma dinâmica! Também serve para "concentrar" a
# criação de várias rotas de forma simples! By John Doe
def add_restful_routes(
        self, 
        name, 
        factory, 
        view=RESTfulView, 
        route_kw=None, 
        view_kw=None
    ):
    """ Add a set of RESTful routes for an entity.

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

    route_kw={} if route_kw is None else route_kw
    view_kw={} if view_kw is None else view_kw
    view_kw.setdefault('http_cache', 0)
    subs=dict(
        name=name, 
        slug=name, 
        id='{id}', 
        renderer='{renderer}'
    )
    perms={
        'GET': 'view', 
        'POST': 'create', 
        'PUT': 'edit', 
        'DELETE': 'delete'
    }

    def add_route(name, pattern, attr, method):
        name=name.format(**subs)
        pattern=pattern.format(**subs)
        self.add_route(
            name, 
            pattern, 
            factory=factory, 
            request_method=method, 
            **route_kw
        )
        if name == 'create_user':
            permission=None
        else:
            permission=perms[method]

        self.add_view(
            view=view, 
            attr=attr, 
            route_name=name, 
            request_method=method, 
            permission=permission
        )

    # NOTE: Get collection! By John Doe
    add_route(
        'get_{name}_collection_rendered', 
        '/{slug}.{renderer}', 
        'get_collection', 
        'GET'
    )

    # NOTE: Cached routes! By John Doe
    add_route(
        'get_{name}_collection_cached', 
        '/cached/{slug}', 
        'get_collection_cached', 
        'GET'
    )

    add_route(
        'get_{name}_cached', 
        '/cached/{slug}/{id}', 
        'get_member_cached', 
        'GET'
    )

    # NOTE: Regular routes! By John Doe
    add_route(
        'get_{name}_collection', 
        '/{slug}', 
        'get_collection', 
        'GET'
    )

    # NOTE: Get member! By John Doe
    add_route(
        'get_{name}_rendered', 
        '/{slug}/{id}.{renderer}', 
        'get_member', 
        'GET'
    )

    add_route(
        'get_{name}', 
        '/{slug}/{id}', 
        'get_member', 
        'GET'
    )

    # NOTE: Create member! By John Doe
    add_route(
        'create_{name}', 
        '/{slug}', 
        'create_member', 
        'POST'
    )

    # NOTE: Update member! By John Doe
    add_route(
        'update_{name}', 
        '/{slug}/{id}', 
        'update_member', 
        'PUT'
    )

    # NOTE I: {slug} e {name} recebem o que vai no parâmetro "name" da chamada!
    # By John Doe

    # NOTE II: Delete member! By John Doe
    add_route(
        'delete_{name}', 
        '/{slug}/{id}', 
        'delete_member', 
        'DELETE'
    )
