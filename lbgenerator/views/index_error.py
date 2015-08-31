
from . import CustomView
from ..model import BASES
from pyramid.response import Response
from sqlalchemy import delete


class IndexErrorCustomView(CustomView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def mapper(self, obj):
        return obj.id_error

    def delete_collection(self):
        """ 
        Delete database collection of objects. This method needs a valid JSON
        query and a valid query path . Will query database objects, and update 
        each path (deleting the respective path). Return count of successes and 
        failures.
        """
        collection = self.get_collection(render_to_response=False)
        in_clause = tuple(map(self.mapper, collection))
        stmt = delete(self.context.entity.__table__).where(
            self.context.entity.__table__.c.id_error.in_(in_clause))
        self.context.session.begin()
        self.context.session.execute(stmt)
        self.context.session.commit()
        self.context.session.close()

        return Response('OK')
