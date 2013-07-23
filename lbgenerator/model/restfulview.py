from pyramid_restler.view import RESTfulView
import json, datetime
from sqlalchemy.schema import Sequence
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from lbgenerator.model.entities import *
from lbgenerator.model.restexception import RestException
from lbgenerator.model.context import RegContextFactory
from lbgenerator.model import base_context

exception = RestException()

def response_callback(request, response):
    if 'callback' in request.params:
        response.text = request.params['callback'] + '(' + response.text + ')'

class CustomView(RESTfulView):

    """ General Customized Views for REST app.
    """
    def __init__(self, *args):
        self.context = args[0]
        self.request = args[1]
        self.request.add_response_callback(response_callback)
        md = self.request.matchdict
        self.base_name = md.get('basename')
        if md.get('id'):
            if not exception.is_integer(md.get('id')):
                exception.throw('id "%s" is not an integer!' %(md.get('id')))

    def get_member(self, render=True):
        id = self.request.matchdict['id']
        if hasattr(self.context.entity, 'json_reg'):
            self.fields = ['json_reg']
        self.wrap = False
        member = self.context.get_member(id)
        if render: return self.render_to_response(member)
        else: return member

    def _get_data(self):
        """ Get all valid data from (request) POST or PUT.
        """
        return self.data

    def _base_context(self):
        """ Get relational fields from base_xml defition.
            This feature helps on mapping tables or creating tables with additional columns.
            Can be used to extract relational-fields values within json_reg too.
        """
        return base_context.get_base(self.base_name)['cc']

    def get_collection(self):
        kwargs = self.request.params.get('$$', {})
        if kwargs:
            kwargs = exception.validate_json(kwargs)
        try:
            collection = self.context.get_collection(**kwargs)
            return self.render_to_response(collection)
        except Exception as e:
            exception.throw('Error trying to complete your search: {}'.format(str(e.args[0])))

    def create_member(self):
        member = self.context.create_member(self._get_data())
        id = self.context.get_member_id_as_string(member)
        headers = {'Location': '/'.join((self.request.path, id))}
        return Response(id, status=201, headers=headers)

    def update_member(self, doc_data=None):
        id = self.request.matchdict['id']
        if doc_data:
            data = doc_data
            index = False
        else:
            data = self._get_data()
            index = True
        member = self.context.update_member(id, data, index=index)
        if member is None:
            raise HTTPNotFound()
        else:
            return Response('UPDATED', charset='utf-8', status=200, content_type='')

    def delete_member(self):
        id = self.request.matchdict['id']
        if hasattr(self.context, 'delete_referenced_docs'):
            self.context.delete_referenced_docs(id)
        member = self.context.delete_member(id)
        if member is None:
            raise HTTPNotFound()
        return Response('DELETED', charset='utf-8', status=200, content_type='')

class BaseCustomView(CustomView):

    """ Customized views for base REST app.
    """
    def __init__(self, *args):
        super(BaseCustomView, self).__init__(*args)
        self.data = exception.validate_base_data(self, args[1])

class RegCustomView(CustomView):

    """ Customized views for reg REST app.
    """
    def __init__(self, *args):
        super(RegCustomView, self).__init__(*args)
        self.seq = Sequence('lb_reg_%s_id_reg_seq' %(self.base_name))
        self.data = exception.validate_reg_data(self, args[1])

    def set_id_up(self, json_reg, id):
        """ Puts id_reg on it's place.
        """
        json_reg['id_reg'] = id
        return json_reg

    def get_cc_data(self, json_reg):
        """ Extracts field values from json_reg if they are relational fields 
        """
        base_cc = self._base_context()
        cc = dict()
        for j in json_reg:
            if j in base_cc['unique_cols']:
                cc[j] = json_reg[j]
            elif j in base_cc['normal_cols']:
                cc[j] = json_reg[j]
        return cc

class DocCustomView(CustomView):

    """ Customized view for doc REST app.
    """
    def __init__(self, *args):
        super(DocCustomView, self).__init__(*args)
        self.seq = Sequence('lb_doc_%s_id_doc_seq' %(self.base_name))
        self.data = exception.validate_doc_data(self, args[1])

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
        self.json_reg = exception.validate_json(db_obj.json_reg)

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
            if fn in self._base_context()['SemIndice']:
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


