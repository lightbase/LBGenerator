import json
import requests
import collections

from pyramid.response import Response

from ..model.context.es import ESContextFactory
from liblightbase.lbutils.codecs import json2object

class LBSearch:
    def __init__(self, request):
        self.request = request

        # get context
        self.context = ESContextFactory(self.request)
        self.context.base_name = self.request.matchdict['base']


    def __call__(self):
        return self.execute_es_query()


    def execute_es_query(self):
        # parse json body
        dict_request = self.request.json_body

        in_source = False
        
        # TODO: validate fields

        # create es query
        dict_es_query = {
            'query': {
                'query_string': {
                    'default_operator': "AND",
                    'query': dict_request['query'],
                    'fields': ['_all']
                }
            }
        }

        if 'highlight' in dict_request:
            self.highlight_req = dict_request['highlight']

            dict_es_query['highlight'] = {
                'fields': {
                    '*': {
                        'number_of_fragments': 10,
                        'fragment_size': 500
                    }
                }
            }

            in_source = dict_request['highlight'].pop('in_source', False)

            dict_es_query['highlight'].update(dict_request['highlight'])


        # if 'override' in dict_request:
        #     dict_es_query = _update_es_query(dict_es_query, dict_request['override'])

        # BEGIN DEBUG
        print(str(dict_es_query))
        # END DEBUG
        url = self.context.get_base().metadata.idx_exp_url
        # path = self.request.matchdict['path']
        # if path: 
            # url += path
        # else:
        url += '/_search'

        json_es_query = json.dumps(dict_es_query)
        response = requests.get(url, data=json_es_query)
        response_text = response.text

        if in_source:
            dict_response = json.loads(response.text)
            if dict_response['hits']['total'] > 0:
                hits = dict_response['hits']['hits']
                for hit in hits:
                    if 'highlight' in hit:
                        for k, v in hit['highlight'].items():
                            self._update_highlight(hit['_source'], k.split('.'), v)
                    hit.pop('highlight')
            response_text = json.dumps(dict_response)


        return Response(response_text, content_type='application/json')

    def _update_highlight(self, source, l_path, hl_values):
        key = l_path.pop(0)

        if len(l_path) == 0:
            if isinstance(source, list):
                # multivalued                        
                for src_value in source:
                    l_path.insert(0, key)
                    self._update_highlight(src_value, l_path, hl_values)
            else:
                # not multivalued
                for hl_value in hl_values:
                    no_hl_value = self._get_no_highlight_value(hl_value)

                    if source[key] == no_hl_value:
                        source[key] = hl_value
                        hl_values.remove(hl_value)
                        break
        else:
            self._update_highlight(source[key], l_path, hl_values)
            

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
