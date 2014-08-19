
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
import requests
from . import CustomView

class ESCustomView(CustomView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.context.base_name = self.request.matchdict['base']

    def get_interface(self):
        params = dict(self.request.params)
        url = self.context.get_base().metadata.idx_exp_url
        path = self.request.matchdict['path']
        if path:
            url += path
        response = requests.get(url, params=params)
        return Response(response.text)

    def post_interface(self):
        url = self.context.get_base().metadata.idx_exp_url
        path = self.request.matchdict['path']
        if path:
            url += path
        response = requests.get(url, data=self.request.body)
        return Response(response.text)
