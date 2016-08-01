
from . import CustomContextFactory
from ..entities import LBIndexError

class IndexErrorContextFactory(CustomContextFactory):
    """Document factory methods."""

    entity = LBIndexError

    def __init__(self, request):
        super(IndexErrorContextFactory, self).__init__(request)

    def delete_member(self, id):
        member = self.get_member(id, close_sess=False)
        if member is None:
            # BEGIN DEBUG
            # self.session.close()
            # END DEBUG
            return None
        self.session.delete(member)
        # BEGIN DEBUG
        # self.session.commit()
        # END DEBUG
        return member
