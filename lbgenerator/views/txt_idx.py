from sqlalchemy import delete
from liblightbase.lbutils import exc
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from pyramid.exceptions import HTTPBadRequest

from . import CustomView
from ..lib.lb_exception import LbException
from ..lib.validation.txt_idx import validate_txt_idx_data


class TxtIdxCustomView(CustomView):
    """ View p/ manipulação dos dados da rota "_txt_idx".
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create_member(self):
        data = validate_txt_idx_data(self, self.request)
        try:
            member = self.context.create_member(data)
            id = self.context.get_member_id_as_string(member)

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            return self.render_custom_response(id, default_response=id)
        except Exception as e:

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            raise LbException(str(e))

    def update_member(self):
        data = validate_txt_idx_data(self, self.request)
        result = self.context.update_member(data)
        if result <= 0:

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            raise HTTPNotFound()
        else:

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            return Response('UPDATED', charset='utf-8', status=200, content_type='')

    def delete_member(self):
        result = self.context.delete_member()
        if result <= 0:

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            raise HTTPNotFound()
        else:

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            return Response('DELETED', charset='utf-8', status=200, content_type='')

    def get_member(self):
        self.wrap = False
        member = self.context.get_member()
        if member == None:

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            raise HTTPNotFound()
        else:

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            return self.render_to_response(member)
