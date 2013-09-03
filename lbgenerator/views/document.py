import json, datetime
from lbgenerator.views import CustomView
from lbgenerator.views.registry import RegCustomView
from sqlalchemy.schema import Sequence
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from lbgenerator.model.context.registry import RegContextFactory
from lbgenerator.lib.validation.document import validate_doc_data
from lbgenerator.lib import utils 

class DocCustomView(CustomView):

    """ Customized view for doc REST app.
    """
    def __init__(self, context, request):
        super(DocCustomView, self).__init__(context, request)
        self.seq = Sequence('lb_doc_%s_id_doc_seq' %(self.base_name))
        self.data = validate_doc_data(self, request)

    def set_json_reg(self):
        """ Set up objects (reg_view, json_reg)
            These objects should be used along doc's request process.
        """
        request = self.request.copy()
        request.matchdict = dict(basename = self.base_name, id = self.id_reg)
        request.method = 'GET'
        self.reg_view = RegCustomView(RegContextFactory(request), request)
        db_obj = self.reg_view.get_member(render=False)
        if not db_obj: raise HTTPNotFound()
        self.json_reg = utils.to_json(db_obj.json_reg)

    def deny_overwrite(self, d):
        if self.request.method == 'POST' and self.is_doc(d):
            if str(d['id_doc']) == '0': pass
            elif d['id_doc'] is None: pass
            else:
                raise Exception('Try PUT to update a document.')

    def config_reg(self, doc, json_reg=None, create=False):
        """ This method updates json_reg (if provided) based on doc data.
            Returns both doc data and json_reg.
        """
        if json_reg:
            fn = doc.pop('_field_name_')
            self.deny_overwrite(json_reg.get(fn))
            doc['id_doc'] = self.context._execute(self.seq)
            json_reg[fn] = dict(
                id_doc = doc['id_doc'],
                nome_doc = doc['nome_doc'],
                mimetype = doc['mimetype'],
                )
            if fn in self.get_base().custom_columns['Nenhum']:
                doc['dt_ext_texto'] = str(datetime.datetime.now())
            return doc, json.dumps(json_reg, ensure_ascii=False)
        return doc, json_reg

    def create_member(self):
        data = self._get_data()
        _doc, _json_reg = self.config_reg(data, json_reg=getattr(self, 'json_reg', None))
        member = self.context.create_member(_doc)
        if _json_reg:
            doc_data = dict(json_reg = _json_reg, dt_index_tex=None)
            self.reg_view.update_member(doc_data)
        id = self.context.get_member_id_as_string(member)
        headers = {'Location': '/'.join((self.request.path, id))}
        return Response(id, status=201, headers=headers)

    def update_member(self):
        id = self.request.matchdict['id']
        data = self._get_data()
        _doc, _json_reg = self.config_reg(data, json_reg=getattr(self, 'json_reg', None))
        member = self.context.update_member(id, _doc)
        if member is None:
            raise HTTPNotFound()
        if _json_reg:
            doc_data = dict(json_reg=_json_reg, dt_index_tex=None)
            self.reg_view.update_member(doc_data)
        return Response('UPDATED', charset='utf-8', status=200, content_type='')

    def is_doc(self, dic, id=None):
        response = False
        if type(dic) is dict and len(dic) == 3:
            doc = 'id_doc' and 'nome_doc' and 'mimetype'
            if id: same_id = int(dic.get('id_doc')) == int(id)
            else: same_id = True
            if doc in dic and same_id:
                response = True
        return response

    def search_doc(self, js, id):
        if type(js) is not dict:
            return None
        for f in js:
            if self.is_doc(js[f], id=id):
                return f

    def delete_from_reg(self, id):
        doc = self.get_member(render=False)
        if doc is None:
            raise HTTPNotFound()
        id_reg = doc[0].id_reg
        self.id_reg = id_reg
        self.set_json_reg()
        referenced_doc = self.search_doc(self.json_reg, id)
        if referenced_doc:
            del self.json_reg[referenced_doc]
            doc_data = dict(
                json_reg=json.dumps(self.json_reg, ensure_ascii=False),
                dt_index_tex=None
                )
            return self.reg_view.update_member(doc_data)

    def delete_member(self):
        id = self.request.matchdict['id']
        self.delete_from_reg(id)
        member = self.context.delete_member(id)
        if member is None:
            raise HTTPNotFound()
        return Response('DELETED', charset='utf-8', status=200, content_type='')
