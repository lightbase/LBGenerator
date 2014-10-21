
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
import requests
from . import CustomView
from ..model.context.document import DocumentContextFactory
from .document import DocumentCustomView
from ..lib.utils import FakeRequest

class ESCustomView(CustomView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.context.base_name = self.request.matchdict['base']

    @staticmethod
    def map_id_doc(es_hits):
        return es_hits['fields']['_metadata.id_doc'][0]

    def get_interface(self):
        params = dict(self.request.params)

        if 'lbquery' in params:
            params.pop('lbquery')
            query_lb = True
        else:
            query_lb = False

        url = self.context.get_base().metadata.idx_exp_url
        path = self.request.matchdict['path']
        if path:
            url += path
        response = requests.get(url, params=params)

        if query_lb:
            response_json = response.json()
            id_docs = repr(tuple(map(self.map_id_doc, response_json['hits']['hits'])))
            if id_docs[-2] == ',':
                id_docs = id_docs[:-2] + ')'
            if id_docs == '())' or id_docs == '(,)' or id_docs == '()':
                id_docs = '(null)'
            mock_request = FakeRequest(
                params = {'$$': '{"literal":"id_doc in %s", "limit":null}}' % (id_docs)},
                matchdict = {'base': self.request.matchdict['base']})
            doc_factory = DocumentContextFactory(mock_request)
            doc_view = DocumentCustomView(doc_factory, mock_request)
            return doc_view.get_collection()

        return Response(response.text, content_type='application/json')

    def post_interface(self):
        url = self.context.get_base().metadata.idx_exp_url
        params = dict(self.request.params)
        if 'lbquery' in params:
            params.pop('lbquery')
            # Note: Seta para que automaticamente o ES retorne só as IDs, no caso do retorno vim do LB! By Questor
            params["fields"] = "_metadata.id_doc"
            query_lb = True
        else:
            query_lb = False
        path = self.request.matchdict['path']
        if path:
            url += path
        # Note: Verificar se esse retorno está coerente, ou seja, se retorna mesmo
        # os 10 registros! By Questor
        response = requests.get(url, params=params, data=self.request.body)

        if query_lb:
            response_json = response.json()
            id_docs = repr(tuple(map(self.map_id_doc, response_json['hits']['hits'])))
            if id_docs[-2] == ',':
                id_docs = id_docs[:-2] + ')'
            if id_docs == '())' or id_docs == '(,)' or id_docs == '()':
                id_docs = '(null)'
            mock_request = FakeRequest(
                params = {'$$': '{"literal":"id_doc in %s", "limit":null}}' % (id_docs)},
                matchdict = {'base': self.request.matchdict['base']})
            doc_factory = DocumentContextFactory(mock_request)
            doc_view = DocumentCustomView(doc_factory, mock_request)
            return doc_view.get_collection()

        return Response(response.text + "{puto: 'puto'}", content_type='application/json')
