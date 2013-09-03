
from lbgenerator.model.context import CustomContextFactory
from lbgenerator.model import get_bases
from lbgenerator.model import doc_hyper_class

class DocContextFactory(CustomContextFactory):

    def __init__(self, request):
        super(DocContextFactory, self).__init__(request)
        if not self.base_name in get_bases():
            raise Exception('Base "%s" does not exist' %(self.base_name))
        self.entity = doc_hyper_class(self.base_name)

    def member_to_dict(self, member, fields=None):
        if fields is None:
            fields = self.default_fields
        host = self.request._host__get()
        obj = dict((name, getattr(member, name)) for name in fields if name != 'blob_doc')
        if 'blob_doc' in self.default_fields:
            id_doc = getattr(member, 'id_doc')
            url_list = ['http:/', host, 'api', 'doc', self.base_name, str(id_doc), 'download']
            url = '/'.join(url_list)
            obj['blob_doc'] = url
        return obj

    def delete_member(self, id):
        member = self.get_member(id, force=True)
        if member is None:
            return None
        self.session.delete(member)
        self.session.commit()
        self.session.close()
        return member
