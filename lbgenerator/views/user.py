import json
import logging

from pyramid.security import forget
from pyramid.response import Response
from pyramid.security import remember
from pyramid.exceptions import HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPOk, HTTPForbidden

from .. import config
from . import CustomView
from .security import verify_api_key
from ..model.context.user import UserContextFactory
from ..lib.validation.user import validate_user_data

# TODO: Armazenar mensagens lugar diferente! By John Doe
USER_PASSWD_INVALID="Username or password invalid"
REQUIRED_PARAM="Required parameters not found in the request : {0}"
USER_ALREADY_EXIST="User {0} already exists!"

log=logging.getLogger(__name__)


def generate_api_key(data):
    import base64
    import hashlib
    import hmac
    id_user=data['id_user']
    return hashlib.sha224(id_user.encode('ascii')).hexdigest()

class UserView(CustomView):
    """
    Views referente ao módulo de Segurança
    """

    def __init__(self, context, request):
        self.context=context
        self.request=request

    def _get_data(self):
        return validate_user_data(self, self.request)

    @verify_api_key
    def create_member(self):
        id_user=self.request.params['id_user']
        same_user=self.context.get_member(id_user)
        if same_user:

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            # TODO: Validações não deveriam "raise exceptions"! By John Doe
            raise Exception(USER_ALREADY_EXIST.format(id_user))

        api_key=generate_api_key(self.request.params)

        # TODO: _get_data poderia receber o json a ser criado, ao invés de 
        # obter da requisição! By John Doe
        data=self._get_data()

        data['api_key']=api_key
        data['document']['api_key']=api_key
        data['value']['api_key']=api_key
        member=self.context.create_member(data)
        id=self.context.get_member_id_as_string(member)
        data_created= {}
        data_created['id_user']=id
        data_created['api_key']=api_key
        response_str=data_created.__str__()

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if self.context.session.is_active:
                self.context.session.close()
        except:
            pass

        # TODO: Send email to new user! By John Doe
        return self.render_custom_response(id, default_response=id)

    @staticmethod
    def validate_params(request, params):
        """
        Valida se em uma request os params foram especifidos
        """
        missing_params=[]
        for param in params:
            value=request.params.get(param)
            if value is None:
                missing_params.append(param)

        return missing_params

    def authenticate(self):
        """
        Autentica um usuário, caso o usuário e senha esteja correto,
        adicionando um cookie para que suas credenciais sejam lembradas
        nas próximas requisiçoes.
        """

        session=self.request.session
        missing_params=self.validate_params(self.request, ['nm_user', 'passwd_user'])
        if len(missing_params) != 0:

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            raise Exception(REQUIRED_PARAM.format(','.join(missing_params)))

        user=self.request.params.get('nm_user')
        passwd=self.request.params.get('passwd_user')

        # TODO: Criptografar a senha, para comparar com a senha criptografada
        # que está armazenada no banco! By John Doe
        if user == config.ADMIN_USER:
            if passwd == config.ADMIN_PASSWD:
                headers=remember(self.request, user)

                # NOTE: Tentar fechar a conexão de qualquer forma!
                # -> Na criação da conexão "coautocommit=True"!
                # By Questor
                try:
                    if self.context.session.is_active:
                        self.context.session.close()
                except:
                    pass

                return Response('OK', headers=headers)
            else:

                # NOTE: Tentar fechar a conexão de qualquer forma!
                # -> Na criação da conexão "coautocommit=True"!
                # By Questor
                try:
                    if self.context.session.is_active:
                        self.context.session.close()
                except:
                    pass

                raise Exception(USER_PASSWD_INVALID)

        member=self.context.get_member(user)
        if not member or member.passwd_user != passwd:

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            raise Exception(USER_PASSWD_INVALID)
        else:
            headers=remember(self.request, user)
            self.request.session['user']=member
            self.request.session.changed()

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            return Response('OK', headers=headers)

    def unauthenticate(self):
        """
        Remove a autenticação do usuário, através da remoção
        do cookie que foi adicionado em ``authenticate``.
        """

        headers=forget(self.request)
        if 'user' in self.request.session:
            del self.request.session['user']

        if 'bases_user' in self.request.session:
            del self.request.session['bases_user']

        self.request.session.changed()

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if self.context.session.is_active:
                self.context.session.close()
        except:
            pass

        return Response('OK', headers=headers)

    def test_login(self):
        logged_in=authenticated_userid(self.request)
        return Response(str(logged_in))
