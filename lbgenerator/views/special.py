from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.exceptions import HTTPNotFound
from pyramid.response import Response
from lbgenerator.model import begin_session
from lbgenerator.model import base_exists
from lbgenerator.model import reg_hyper_class
from lbgenerator.model import doc_hyper_class
from lbgenerator.lib import utils
import json
import datetime

@view_defaults(route_name='text')
class DocText(object):

    def __init__(self, request):
        self.request = request
        self.base_name = request.matchdict.get('base')
        self.id_doc = request.matchdict.get('id')
        if not base_exists(self.base_name):
            raise Exception('Base does not exist!')
        self.doc_entity = doc_hyper_class(self.base_name)
        self.reg_entity = reg_hyper_class(self.base_name)
        self.session = begin_session()

    def get_text(self, id_doc):
        response = self.session.query(self.doc_entity.texto_doc).filter_by(id_doc=id_doc).first()
        if response is None:
            raise HTTPNotFound()
        self.session.close()
        return response[0]

    @view_config(request_method='GET')
    def get(self):
        text = self.get_text(self.id_doc)
        response = {'texto_doc': text}
        return Response(json.dumps(response, ensure_ascii=True), content_type='application/json')

    @view_config(request_method='POST')
    def post(self):
        params = self.request.params
        if not 'texto_doc' in params:
            raise Exception('Required param: texto_doc')

        doc = self.session.query(self.doc_entity).get(self.id_doc)
        if not doc:
            raise HTTPNotFound()

        reg = self.session.query(self.reg_entity).get(doc.id_reg)
        if not reg:
            raise HTTPNotFound()

        text = params.get('texto_doc')
        doc.texto_doc = text
        doc.dt_ext_texto = str(datetime.datetime.now())
        if text != 'nulo':
            reg.dt_index_tex = None

        self.session.commit()
        self.session.close()
        return Response('UPDATED', content_type='application/json')




