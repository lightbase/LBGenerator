
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
            # Now commits and closes session in the view instead of here
            return None
        self.session.delete(member)
        # Now commits and closes session in the view instead of here
        return member
