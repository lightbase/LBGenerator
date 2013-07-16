# -*- coding: utf-8 -*-
from lbgenerator.model import root_view
from lbgenerator.model.context import (
                                      BaseContextFactory,
                                      FormContextFactory,
                                      RegContextFactory,
                                      DocContextFactory
                                      )
from lbgenerator.model.restfulview import BaseCustomView, RegCustomView, DocCustomView


def make_routes(config):
    """
    Cria rotas para aplicação do gerador de bases
    """

    #   ***REST API***

    # not really required
    config.add_route('api', '/api')
    config.add_view(route_name='api', view=root_view, renderer='rest.mako')

    # restful routes
    config.add_restful_routes('api/base', BaseContextFactory, view=BaseCustomView)
    config.add_restful_routes('api/form', FormContextFactory)
    config.add_restful_routes('api/reg/{basename}', RegContextFactory, view=RegCustomView)
    config.add_restful_routes('api/doc/{basename}', DocContextFactory, view=DocCustomView)
    config.enable_POST_tunneling()

    #   ***Home***
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    #   ***Base***

    config.add_route('new_base',     'lb/new')

    config.add_route('view_base',    'lb/{base_name}/view')
    config.add_route('edit_base',    'lb/{base_name}/edit')
    config.add_route('delete_base',  'lb/{base_name}/delete')

    #   ***Formulário***

    config.add_route('new_form',     'lb/{base_name}/form/new')
    config.add_route('edit_form',    'lb/{base_name}/form/{form_name}/edit')
    config.add_route('delete_form',  'lb/{base_name}/form/{form_name}/delete')

    #   ***Registro***

    config.add_route('new_reg',      'lb/{base_name}/reg/{form_name}/new')
    config.add_route('view_reg',     'lb/{base_name}/reg/{form_name}/view/{id_reg}')
    config.add_route('edit_reg',     'lb/{base_name}/reg/{form_name}/edit/{id_reg}')
    config.add_route('delete_reg',   'lb/{base_name}/reg/{form_name}/delete/{id_reg}')

    #   ***Métodos especiais***

    config.add_route('full_reg', 'api/reg/{base_name}/{id_reg}/full')
    config.add_route('download', 'api/doc/{base_name}/{id_doc}/download')
    config.add_route('text', 'api/doc/{base_name}/{id_doc}/text')






