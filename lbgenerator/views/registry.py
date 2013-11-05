
from sqlalchemy.schema import Sequence
from lbgenerator.views import CustomView
from lbgenerator.lib.validation.registry import validate_reg_data
from lbgenerator.lib import utils
from lbgenerator.model import doc_hyper_class
from lbgenerator.model.index import Index
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
import json

class RegCustomView(CustomView):

    """ Customized views for reg REST app.
    """
    def __init__(self, context, request):
        super(RegCustomView, self).__init__(context, request)
        self.data = validate_reg_data(self, request)
        self.context.index = Index(self.base_name, self.full_reg)

    def get_member(self):
        id = self.request.matchdict['id']
        self.fields = ['json_reg']
        self.wrap = False
        member = self.context.get_member(id)
        return self.render_to_response(member)

    def delete_member(self):
        id = self.request.matchdict['id']
        self.context.delete_referenced_docs(id)
        member = self.context.delete_member(id)
        if member is None:
            raise HTTPNotFound()
        return Response('DELETED', charset='utf-8', status=200, content_type='')

    def get_cc_data(self, json_reg):
        """ Extracts field values from json_reg if they are relational fields 
        """
        base_cc = self.get_base().custom_columns
        cc = dict()
        for j in json_reg:
            if j in base_cc['unique_cols']:
                cc[j] = json_reg[j]
            elif j in base_cc['normal_cols']:
                cc[j] = json_reg[j]
        return cc

    def get_response_text(self, response):
        response.content_type='text/html'
        response.charset='utf-8'
        return response.text

    def get_path(self):
        member = self.get_db_obj()
        if member is None:
            raise HTTPNotFound()
        base = self.get_base()
        value = base.get_path(member.json_reg, self.request.matchdict['path'])
        return Response(value, content_type='application/json')

    def set_path(self):
        member = self.get_db_obj()
        if member is None:
            raise HTTPNotFound()
        base = self.get_base()
        path, value = self.request.matchdict['path'], self.request.params['value']
        index, registry = base.set_path(member.json_reg, path, value)
        id = int(self.request.matchdict['id'])
        self.data = dict(json_reg= base.validate(utils.to_json(registry), id))
        response = self.update_member()
        response_text = self.get_response_text(response)
        if response.text == 'UPDATED':
            return Response(str(index), charset='utf-8', status=200, content_type='')
        else:
            return Response(response.text, status=500)

    def put_path(self):
        member = self.get_db_obj()
        if member is None:
            raise HTTPNotFound()
        base = self.get_base()
        path, value = self.request.matchdict['path'], self.request.params['value']
        registry = base.put_path(member.json_reg, path, value)
        id = int(self.request.matchdict['id'])
        self.data = dict(json_reg= base.validate(utils.to_json(registry), id))
        response = self.update_member()
        response_text = self.get_response_text(response)
        if response.text == 'UPDATED':
            #return Response(self.get_db_obj().json_reg, charset='utf-8', status=200, content_type='')
            return Response(self.get_db_obj().json_reg, content_type='application/json')
        else:
            return Response(response.text, status=500)

    def delete_path(self):
        member = self.get_db_obj()
        if member is None:
            raise HTTPNotFound()
        base = self.get_base()
        path = self.request.matchdict['path']
        registry = base.delete_path(member.json_reg, path)
        id = int(self.request.matchdict['id'])
        self.data = dict(json_reg= base.validate(utils.to_json(registry), id))
        response = self.update_member()
        response_text = self.get_response_text(response)
        if response.text == 'UPDATED':
            #return Response(self.get_db_obj().json_reg, charset='utf-8', status=200, content_type='')
            return Response(self.get_db_obj().json_reg, content_type='application/json')
        else:
            return Response(response.text, status=500)

    def full_reg(self):
        registry = utils.to_json(self.get_db_obj().json_reg)
        registry = self.context.get_full_reg(registry)
        return Response(json.dumps(registry, ensure_ascii=False), content_type='application/json')


