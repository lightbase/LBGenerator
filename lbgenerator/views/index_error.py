from . import CustomView
from ..model import BASES
from sqlalchemy import delete
from pyramid.response import Response


class IndexErrorCustomView(CustomView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def mapper(self, obj):
        return obj.id_error

    def delete_collection(self):
        """Delete database collection of objects. This method needs a valid JSON
        query and a valid query path . Will query database objects, and update 
        each path (deleting the respective path). Return count of successes and 
        failures.
        """

        collection=self.get_collection(render_to_response=False)
        in_clause=tuple(map(self.mapper, collection))
        stmt=delete(self.context.entity.__table__).where(
            self.context.entity.__table__.c.id_error.in_(in_clause))

        # TODO: Talvez seja necessário um "begin" e um "commit" aqui!
        # By Questor
        # self.context.session.begin()
        # self.context.session.commit()

        self.context.session.execute(stmt)

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if self.context.session.is_active:
                self.context.session.close()
        except:
            pass

        return Response('OK')
