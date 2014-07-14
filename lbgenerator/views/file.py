import uuid, cgi
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

    def get_size(self, fileobject):
        """ Get file size in bytes. 
        """
        # move the cursor to the end of the file
        fileobject.seek(0, 2)
        size = fileobject.tell()
        # move the cursor to the begin of the file
        fileobject.seek(0)
        return size

    def build_file_data(self, filename, mimetype, input_file):
        """ 
        @param filename:
        @param mimetype:
        @param input_file:
        Return filemask (dictionay) and file member (dictionay), used
        to instaciate with mapped entity.
        """

        filemask = {
           'uuid': str(uuid.uuid4()),
           'filename': filename,
           'filesize': self.get_size(input_file),
           'mimetype': mimetype,
        }

        namespace = uuid.UUID(filemask['uuid'])
        name = str(hash(frozenset(filemask.items())))
        id_file = str(uuid.uuid3(namespace, name))
        filemask['id_file'] = id_file

        member = {
           'id_doc': None,
           'file': input_file.read(),
           'filetext': None,
           'dt_ext_text': None
        }

        member.update(filemask)
        member.pop('uuid')
        return member, utils.object2json(filemask)

    ###########################
    # FILE MEMBERS OPERATIONS #
    ###########################

    def get_member(self):
        id = self.request.matchdict['id']
        member = self.context.get_member(id)
        self.wrap = False
        return self.render_to_response(member)

    def create_member(self):
        file_ = self.request.params.get('file')
        if file_ is None:
            raise Exception('Required param file not found in request.')
        elif not isinstance(file_, cgi.FieldStorage):
            raise Exception('Required param file is not a file object.')
        else:
            member, filemask = self.build_file_data(file_.filename,
                                                    file_.type,
                                                    file_.file)
            member = self.context.create_member(member)
            return Response(filemask, content_type='application/json',
                status=201)

    def update_member(self):
        raise NotImplementedError('NOT IMPLEMENTED')

    def delete_member(self):
        raise NotImplementedError('NOT IMPLEMENTED')

    ##############################
    # FILE COLLECTION OPERATIONS #
    ##############################

    def update_collection(self):
        raise NotImplementedError('NOT IMPLEMENTED')

    def delete_collection(self):
        raise NotImplementedError('NOT IMPLEMENTED')

    ########################
    # FILE PATH OPERATIONS #
    ########################

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
        member = self.context.session.query(column).filter(self.context.entity\
            .id_file==id_file).first()

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

        content_disposition = 'filename=' + member.filename
        disposition = self.request.params.get('disposition')
        if disposition and disposition in ('inline', 'attachment'):
            content_disposition = disposition + ';' + content_disposition

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
