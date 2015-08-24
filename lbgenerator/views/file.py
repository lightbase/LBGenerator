#coding: utf-8
import requests
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from . import CustomView
from .. import config
from ..lib.validation.file import validate_file_data
from ..lib import utils


class FileCustomView(CustomView):
    """ Documents Customized View Methods
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.base_name = self.request.matchdict.get('base')

    def _get_data(self):
        """ Get all valid data from (request) POST or PUT.
        """
        return validate_file_data(self, self.request)

    def get_member(self):
        id = self.request.matchdict['id']
        member = self.context.get_member(id)
        self.wrap = False
        return self.render_to_response(member)

    def create_member(self):
        data, filemask = self._get_data()
        member = self.context.create_member(data)
        return Response(filemask,
                        content_type='application/json',
                        status=201)

    def update_member(self):
        raise NotImplementedError('NOT IMPLEMENTED')

    def delete_member(self):
        raise NotImplementedError('NOT IMPLEMENTED')

    def update_collection(self):
        raise NotImplementedError('NOT IMPLEMENTED')

    def delete_collection(self):

        return Response("ok")

    __paths__ = [
        "id_file",
        "id_doc",
        "filename",
        "filesize",
        "mimetype",
        "filetext",
        "download",
        "dt_ext_text",
    ]

    def get_path(self):

        id_file = self.request.matchdict['id']
        path = self.request.matchdict['path']
        if path not in self.__paths__:
            raise Exception('Not a valid path')

        if path == 'download':
            return self._download_file()

        # Get raw mapped entity object.
        column = self.context.entity.__table__.c.get(path)
        member = self.context.session.query(column).filter(self.context.entity \
                                                           .id_file == id_file).first()

        if member is None:
            raise HTTPNotFound()

        return Response(
            utils.object2json(getattr(member, path)),
            content_type='application/json'
        )

    def _download_file(self):
        """ Returns file bytes stream, so user can download it.
        """
        id = self.request.matchdict.get('id')
        member = self.context.get_raw_member(id)
        if member is None:
            raise HTTPNotFound()
        member_encoded = member.filename.encode('latin-1', 'ignore').decode('utf-8', 'ignore')
        content_disposition = 'filename=' + member_encoded
        disposition = self.request.params.get('disposition')
        if disposition and disposition in ('inline', 'attachment'):
            content_disposition = disposition + ';' + content_disposition

        content_disposition = content_disposition.encode('latin-1', 'ignore').decode('utf-8', 'ignore')

        return Response(
            content_type=member.mimetype,
            content_disposition=content_disposition,
            app_iter=[member.file]
        )

    def create_path(self):
        raise NotImplementedError('Create file path operation is not possible')

    def update_path(self):
        raise NotImplementedError('NOT IMPLEMENTED')

    def delete_path(self):
        raise NotImplementedError('Delete file path operation is not possible')

