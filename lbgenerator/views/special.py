import datetime

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.view import view_defaults
from pyramid.exceptions import HTTPNotFound

from ..lib import utils
from ..model import file_entity
from ..model import begin_session
from ..model import document_entity


@view_defaults(route_name='text')
class DocText(object):

    def __init__(self, request):
        self.request = request
        self.base_name = request.matchdict.get('base')
        self.pk = request.matchdict.get('id')
        self.doc_entity = document_entity(self.base_name)
        self.file_entity = file_entity(self.base_name)
        self.session = begin_session()

    def get_text(self, pk):
        response = self.session.query(self.file_entity.filetext)\
            .filter_by(id_file=pk).first()
        if response is None:
            raise HTTPNotFound()
        self.session.close()
        return response[0]

    @view_config(request_method='GET')
    def get(self):
        text = self.get_text(self.pk)
        response = {'filetext': text}
        return Response(utils.object2json(response), content_type='application/json')

    @view_config(request_method='PUT')
    def put(self):
        params = self.request.params
        if not 'filetext' in params:
            raise Exception('Required param: filetext')

        file_ = self.session.query(self.file_entity)\
            .filter_by(id_file=self.pk).first()
        if not file_:
            raise HTTPNotFound()

        document = self.session.query(self.doc_entity).get(file_.id_doc)
        if not document:
            raise HTTPNotFound()

        filetext = params.get('filetext')
        file_.filetext = filetext
        file_.dt_ext_text = datetime.datetime.now()
        if filetext != '':
            document.dt_idx = None
            document.dt_last_up = file_.dt_ext_text

        self.session.commit()
        self.session.close()
        return Response('UPDATED', content_type='application/json')
