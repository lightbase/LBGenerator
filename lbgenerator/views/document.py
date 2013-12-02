import json
import datetime
import uuid
import os
import glob
import cgi
import base64
from lbgenerator.views import CustomView
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from lbgenerator import config
from lbgenerator.lib.validation.document import validate_doc_data
from lbgenerator.lib import utils

class DocCustomView(CustomView):

    """ Documents Customized View Methods
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.base_name = self.request.matchdict.get('base')
        self.data = validate_doc_data(self, request)
        self.tmp_dir = config.TMP_DIR + '/lightbase_tmp_storage/' + self.base_name

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
            data = input_file.read(2<<16)
            if not data:
                break
            output_file.write(data)
        # If your data is really critical you may want to force it to disk first
        # using output_file.flush(); os.fsync(output_file.fileno())
        output_file.close()
        # Now that we know the file has been fully saved to disk move it into place.
        os.rename(tmp_file_path, file_path)
        return str(file_id)

    def get_member(self):
        id = self.request.matchdict['id']
        member = self.context.get_member(id)
        self.wrap = False
        return self.render_to_response(member)

    def create_member(self):
        if self.request.params:
            for k, v in self.request.params.items():
                if isinstance(v, cgi.FieldStorage):
                    filename = v.filename
                    mimetype = v.type
                    input_file = v.file
                    file_id = self.build_storage(filename, mimetype, input_file)
            return Response(file_id, status=201)
        return Response(status=200)

    def update_member(self):
        return Response('NOT IMPLEMENTED', charset='utf-8', status=500, content_type='')

    def delete_member(self):
        return Response('NOT IMPLEMENTED', charset='utf-8', status=500, content_type='')
        """
        storage = self.request.matchdict['id']
        try:
            for filename in glob.glob(self.tmp_dir + '/' + storage + '*'):
                os.remove(filename)
            return Response(status=200)
        except:
            return Response(status=500)
        """

    def download(self):
        """ Returns file bytes stream, so user can download it.
        """
        id = self.request.matchdict.get('id')
        member = self.context.get_raw_member(id)
        if member is None:
            raise HTTPNotFound()

        cd = 'filename=' + member.nome_doc
        params = self.request.params
        if params.get('disposition'):
            if params['disposition'] == 'attachment':
                cd = 'attachment;' + cd
            elif params['disposition'] == 'inline':
                cd = 'inline;' + cd

        return Response(
            content_type=member.mimetype,
            content_disposition=cd,
            app_iter=[member.blob_doc]
        )
