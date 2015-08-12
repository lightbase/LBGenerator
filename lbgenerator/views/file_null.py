# -*- coding: utf-8 -*-

from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from . import CustomView


class FileNullCustonView(CustomView):

    def __init__(self):
        self.context = context
        self.request = request
        self.base_name = self.request.matchdict.get('base')


    def get_null_file(self):
        """
        :return: Retorna busca nos aquivos com id_doc = null
        """

        return Response('ok')

