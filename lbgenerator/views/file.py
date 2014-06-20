import uuid, os, cgi, base64
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
        self.tmp_dir = config.TMP_DIR + '/lightbase_tmp_storage/' + self.base_name

    def _get_data(self):
        """ Get all valid data from (request) POST or PUT.
        """
        return validate_file_data(self, self.request)

    def build_storage(self, filename, mimetype, input_file):
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

        file_id = uuid.uuid4()
        safe_filename = base64.urlsafe_b64encode(filename.encode('utf-8'))
        _filename = '%s.%s.%s' % (file_id, mimetype.replace('/', '-'), safe_filename.decode('utf-8'))

        file_path = os.path.join(self.tmp_dir, _filename)

        tmp_file_path = file_path + '~'
        output_file = open(tmp_file_path, 'wb')
        # Finally write the data to a temporary file
        input_file.seek(0)
        while True:
            data = input_file.read()
            if not data:
                break
            output_file.write(data)
        # If your data is really critical you may want to force it to disk first
        # using output_file.flush(); os.fsync(output_file.fileno())
        output_file.close()
        # Now that we know the file has been fully saved to disk move it into place.
        os.rename(tmp_file_path, file_path)
        return str(file_id)

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
            file_uuid = self.build_storage(file_.filename,
                                           file_.type,
                                           file_.file)
            return Response(file_uuid, status=201)

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
