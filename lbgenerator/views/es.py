
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
import requests
from . import CustomView
from ..model.context.document import DocumentContextFactory
from .document import DocumentCustomView
from ..lib.utils import FakeRequest
from liblightbase.lbutils.codecs import json2object

class ESCustomView(CustomView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.context.base_name = self.request.matchdict['base']

    @staticmethod
    def map_id_doc(es_hits):
        return es_hits['fields']['_metadata.id_doc'][0]
        
    # ToDo: Ajustar para que tenha o mesmo comportamento do método "post_interface",
    # pois do jeito que está vai dar bug! By Questor
    def get_interface(self):
        params = dict(self.request.params)

        if 'lbquery' in params:
            params.pop('lbquery')
            # Note: Seta para que automaticamente o ES retorne só as IDs, no caso
            # do retorno vir do LB! By Questor
            params["fields"] = "_metadata.id_doc"
            dict_query = json2object(self.request.body.decode("utf-8"))
            limit = dict_query['size']
            offset = dict_query['from']
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
            doc_view_get_collection = doc_view.get_collection().json()
            doc_view_get_collection['offset'] = offset
            doc_view_get_collection['limit'] = limit
            return doc_view_get_collection

        return Response(response.text, content_type='application/json')

    def post_interface(self):
        url = self.context.get_base().metadata.idx_exp_url
        params = dict(self.request.params)
        if 'lbquery' in params:
            params.pop('lbquery')
            # Note: Seta para que automaticamente o ES retorne só as IDs, no caso
            # do retorno (OL) vir do LB! By Questor
            params["fields"] = "_metadata.id_doc"
            # Note: Obtém os parâmetros size e from enviados na query ES para 
            # setar no retorno do LB! By Questor
            dict_query = json2object(self.request.body.decode("utf-8"))
            limit = dict_query.get('size', None)
            offset = dict_query.get('from', None)
            query_lb = True
        else:
            query_lb = False
        path = self.request.matchdict['path']
        if path: url += path

        # Make the request
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

            collection = doc_view.get_collection(
                render_to_response=False)

            if limit is not None:
                doc_factory.default_limit = int(limit)
            if offset is not None:
                doc_factory.default_offset = int(offset)

            # Note: Serve para setar o total de ocorrências no 
            # retorno do LB qdo a pesquisa vem do ES! By Questor
            doc_factory.total_count = int(response_json['hits']['total'])

            return doc_view.render_to_response(collection)

        return Response(response.text, content_type='application/json')

    def delete_interface(self):
        params = dict(self.request.params)
        url = self.context.get_base().metadata.idx_exp_url
        path = self.request.matchdict['path']
        if path:
            url += path
        response = requests.delete(url, params=params, data=self.request.body)
        return Response(response.text, content_type='application/json')
