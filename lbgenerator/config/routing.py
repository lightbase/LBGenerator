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

    config.add_static_view('static', 'static', cache_max_age=3600)

    #   ***REST API***
    config.add_restful_routes('base', BaseContextFactory, view=BaseCustomView)
    config.add_restful_routes('reg/{basename}', RegContextFactory, view=RegCustomView)
    config.add_restful_routes('doc/{basename}', DocContextFactory, view=DocCustomView)
    config.enable_POST_tunneling()


    #   ***Métodos especiais***

    config.add_route('path', 'reg/{base}/{id}/path')
    config.add_route('delete_path', 'reg/{base}/{id}/path/{name}')

    config.add_route('full_reg', 'reg/{base_name}/{id_reg}/full')

    config.add_route('download', 'doc/{base_name}/{id_doc}/download')

    config.add_route('text', 'doc/{base_name}/{id_doc}/text')





