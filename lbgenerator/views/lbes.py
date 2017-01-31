import json
import re
import requests
import collections

from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPServiceUnavailable

from ..model.context.es import ESContextFactory
from liblightbase.lbutils.codecs import json2object


class LBSearch:
    valid_fields = ['query', 'search_fields', 'return_fields', 'highlight',
                    'from', 'size', 'sort', 'raw_es_response']

    def __init__(self, request):
        self.request = request

        # get context
        self.context = ESContextFactory(self.request)
        self.context.base_name = self.request.matchdict['base']

    def __call__(self):
        return self.execute_es_query()

    def execute_es_query(self):
        dict_request = self.request.json_body

        # check if fields are valid
        for k, v in dict_request.items():
            if k not in LBSearch.valid_fields:
                return HTTPBadRequest(body="Invalid field: '{}'".format(k))

        # check if query field exists
        if 'query' not in dict_request:
            return HTTPBadRequest(body="No 'query' field")

        # default fields
        raw_es_response = False
        hl_in_source = False
        offset_from = 0
        offset_size = 10
        sort = ['_score']

        # override required fields
        if 'raw_es_response' in dict_request:
            raw_es_response = dict_request['raw_es_response']

        if 'from' in dict_request:
            offset_from = dict_request['from']

        if 'size' in dict_request:
            offset_size = dict_request['size']

        if 'sort' in dict_request:
            sort = dict_request['sort']
            if '_score' not in sort:
                sort.append('_score')

        # create es query
        dict_es_query = {
            'from': offset_from,
            'size': offset_size,
            'sort': sort
        }

        # check for optional fields
        if 'return_fields' in dict_request:
            dict_es_query['_source'] = dict_request['return_fields']

        if 'highlight' in dict_request:
            self.highlight_req = dict_request['highlight']

            dict_es_query['highlight'] = {
                'fields': {
                    '*': {
                        'number_of_fragments': 30,
                        'fragment_size': 1
                    }
                }
            }

            hl_in_source = dict_request['highlight'].pop('in_source', False)

            dict_es_query['highlight'].update(dict_request['highlight'])

        # check type of query
        query = dict_request['query']
        if isinstance(query, str):
            self._build_query_string(dict_es_query, dict_request)
        elif isinstance(query, dict):
            self._build_bool_query(dict_es_query, dict_request)

        base_url = self.context.get_base().metadata.idx_exp_url
        if not base_url:
            return HTTPServiceUnavailable(body='This base is not indexed yet.')

        url = base_url + '/_search'

        json_es_query = json.dumps(dict_es_query)
        response = requests.get(url, data=json_es_query)
        response_text = response.text
        dict_response = json.loads(response_text)

        if 'hits' not in dict_response:
            raise Exception('ES Error: ' + dict_response['error'])

        if hl_in_source:
            if dict_response['hits']['total'] > 0:
                hits = dict_response['hits']['hits']
                for hit in hits:
                    if 'highlight' in hit:
                        for k, v in hit['highlight'].items():
                            hit['_source'] = self._update_highlight(hit['_source'], k.split('.'), v)
                        hit.pop('highlight')

        if not raw_es_response:
            new_dict_response = list()
            hits = dict_response['hits']['hits']
            for hit in hits:
                new_hit = dict()
                new_hit['id_doc'] = hit['_id']
                new_hit['score'] = hit['_score']
                new_hit['data'] = hit['_source']
                new_dict_response.append(new_hit)
                if not hl_in_source and 'highlight' in hit:
                    new_hit['highlight'] = hit['highlight']
            dict_response = new_dict_response

        response_text = json.dumps(dict_response)
        return Response(response_text, content_type='application/json')

    def _build_query_string(self, dict_es_query, dict_request):
        query = re.escape(dict_request['query'])
        query = query.replace('\\ ', ' ')

        # default fields
        search_fields = ['_all']

        # override default fields
        if 'search_fields' in dict_request:
            search_fields = dict_request['search_fields']

        # create es query
        dict_es_query['query'] = {
            'query_string': {
                'default_operator': "AND",
                'query': query,
                'fields': search_fields
            }
        }

        return dict_es_query

    def _build_bool_query(self, dict_es_query, dict_request):
        query = dict_request['query']

        bool_query = {
            'bool': {
                'must': []
            }
        }

        for key, value in query.items():
            value = re.escape(value)
            value = value.replace('\\ ', ' ')
            bool_query['bool']['must'].append({
                'match': {
                    key: value
                }
            })

        dict_es_query['query'] = bool_query

        return dict_es_query

    def _update_highlight(self, source, l_path, hl_values):
        if isinstance(source, dict):
            # group
            key = l_path.pop(0)
            if key in source:
                source[key] = self._update_highlight(source[key], l_path, hl_values)
        elif isinstance(source, list):
            # multivalued
            for idx, item in enumerate(source):
                source[idx] = self._update_highlight(item, l_path, hl_values)
        elif isinstance(source, str):
            for hl_value in hl_values:
                # text value
                no_hl_value = self._get_no_highlight_value(hl_value)
                source = source.replace(no_hl_value, hl_value)

        return source
     
    def _get_no_highlight_value(self, value):
        result = value

        if 'pre_tags' in self.highlight_req:
            for pre_tag in self.highlight_req['pre_tags']:
                result = result.replace(pre_tag, '')
        else:
            result = result.replace('<em>', '')

        if 'post_tags' in self.highlight_req:
            for post_tag in self.highlight_req['post_tags']:
                result = result.replace(post_tag, '')
        else:
            result = result.replace('</em>', '')

        return result

    def _update_es_query(self, original, override):
        for k, v in override.items():
            if isinstance(v, collections.Mapping):
                r = _update_es_query(original.get(k, {}), v)
                original[k] = r
            else:
                original[k] = override[k]

        return original
