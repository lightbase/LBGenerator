from sqlalchemy.util import KeyedTuple
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
        self.default_query = True
        # We don't want to query hole file when searching ..
        cols = [column for column in self.entity.__table__.c if column.name != 'blob_doc']
        q = self.session.query(*cols).filter(self.entity.__table__.c.id_doc==id).all()
        return q or None

    def get_raw_member(self, id):
        return self.session.query(self.entity).get(id)

    def member_to_dict(self, member, fields=None):
        if not isinstance(member, KeyedTuple):
            member = self.member2KeyedTuple(member)
        dict_member = member._asdict()
        if 'blob_doc' in dict_member or self.default_query is True:
            id_doc = dict_member['id_doc']
            dict_member['blob_doc'] = self.download_url(id_doc)
        return dict_member

    def download_url(self, id_doc):
        path_split = self.request.path_url.split('/')
        if path_split[len(path_split) -1 ] == str(id_doc):
            complete = '/download'
        else:
            complete = '/' + str(id_doc) + '/download'
        return self.request.path_url + complete

