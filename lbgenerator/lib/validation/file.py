
from .. import utils
from pyramid.exceptions import NotFound
from .superclass import RequestValidation
import cgi
import uuid

def validate_file_data(view, request):
    """
    @param view:
    @param request:
    """
    return FileData(view, request).get_valid_data()


class FileData(RequestValidation):

    """ File entity request validation
    """

    def get(self):
        """ Get valid data from HTTP GET.
        """
        return None

    def post(self):
        """ Get valid data from HTTP POST.
        """
        file_ = self.verify_param('file', cgi.FieldStorage)
        data, filemask = self.build_post_data(file_)
        return data, filemask

    def put(self):
        """ Get valid data from HTTP PUT.
        """
        pass

    def delete(self):
        """ Get valid data from HTTP DELETE.
        """
        pass

    def build_post_data(self, file_):
        """ 
        Return filemask (dictionay) and file data (dictionay), used
        to instaciate with mapped entity.
        @param file_:
        """

        filemask = {
           'uuid': str(uuid.uuid4()),
           'filename': file_.filename,
           'filesize': self.get_size(file_.file),
           'mimetype': file_.type,
        }

        namespace = uuid.UUID(filemask['uuid'])
        name = str(hash(frozenset(filemask.items())))
        id_file = str(uuid.uuid3(namespace, name))
        filemask['id_file'] = id_file

        data = {
           'id_doc': None,
           'file': file_.file.read(),
           'filetext': None,
           'dt_ext_text': None
        }

        data.update(filemask)
        data.pop('uuid')
        return data, utils.object2json(filemask)

    def get_size(self, fileobject):
        """ Get file size in bytes. 
        """
        # move the cursor to the end of the file
        fileobject.seek(0, 2)
        size = fileobject.tell()
        # move the cursor to the begin of the file
        fileobject.seek(0)
        return size



