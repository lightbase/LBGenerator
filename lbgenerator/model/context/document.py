
from lbgenerator.model.context import CustomContextFactory
from lbgenerator.model import get_bases
from lbgenerator.model import doc_hyper_class

class DocContextFactory(CustomContextFactory):

    def __init__(self, request):
        super(DocContextFactory, self).__init__(request)
        if not self.base_name in get_bases():
            raise Exception('Base "%s" does not exist' %(self.base_name))
        self.entity = doc_hyper_class(self.base_name)

    def get_member(self, id):
        q = self.session.query(self.entity)
        return q.get(id)

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

    def delete_member(self, id):
        member = self.get_member(id)
        if member is None:
            return None
        self.session.delete(member)
        self.session.commit()
        self.session.close()
        return member
