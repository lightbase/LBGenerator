from sqlalchemy.util import KeyedTuple
from . import CustomContextFactory
from .. import file_entity

class FileContextFactory(CustomContextFactory):

    """ Document Factory Methods
    """

    def __init__(self, request):
        super(FileContextFactory, self).__init__(request)
        self.entity = file_entity(self.base_name)

    def get_member(self, id):
        self.single_member = True
        # We don't want to query hole file when searching ..
        # So the bytes column will not be in query list this time.
        cols = [column for column in self.entity.__table__.c \
            if column.name != 'file']
        q = self.session.query(*cols).filter(self.entity\
            .__table__.c.id_file==id).all()
        return q or None

    def member_to_dict(self, member, fields=None):
        if not isinstance(member, KeyedTuple):
            member = self.member2KeyedTuple(member)

        dict_member = member._asdict()

        fields = getattr(self,'_query', {}).get('select')
        if fields and not '*' in fields:
            if 'download' in fields:
                id_file = dict_member['id_file']
                dict_member['download'] = self.download_url(id_file)
            return {field: dict_member[field] for field in fields}

        elif not 'file' in dict_member:
            id_file = dict_member['id_file']
            dict_member['download'] = self.download_url(id_file)

        return dict_member

    def download_url(self, pk):
        path_split = self.request.path_url.split('/')
        if path_split[len(path_split) -1 ] == str(pk):
            complete = '/download'
        else:
            complete = '/' + str(pk) + '/download'
        return self.request.path_url + complete

