
from lbgenerator.model.context import CustomContextFactory
from lbgenerator.model import get_bases
from lbgenerator.model import doc_hyper_class
import json

class DocContextFactory(CustomContextFactory):

    """ Document Factory Methods
    """

    def __init__(self, request):
        super(DocContextFactory, self).__init__(request)
        if not self.base_name in get_bases():
            raise Exception('Base "%s" does not exist' %(self.base_name))
        self.entity = doc_hyper_class(self.base_name)

    def get_member(self, id):
        self.single_member = True
        # We don't want to query hole file when searching ..
        q = self.session.query(*self.get_cols()).filter_by(id_doc=id).all()
        return q or None

    def get_raw_member(self, id):
        return self.session.query(self.entity).get(id)

    def member_to_dict(self, member, fields=None):
        if fields is None:
            fields = self.default_fields
        obj = dict((name, getattr(member, name)) for name in fields if name != 'blob_doc')
        if 'blob_doc' in self.default_fields:
            id_doc = getattr(member, 'id_doc')
            path_split = self.request.path_url.split('/')
            if path_split[len(path_split) -1 ] == str(id_doc):
                complete = '/download'
            else:
                complete = '/' + str(id_doc) + '/download'
            url = self.request.path_url + complete
            obj['blob_doc'] = url
        return obj

