import json

import requests
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound

from ..lib import utils
from ..lib import cache
from . import CustomView
from .security import verify_api_key
from ..lib.validation.base import validate_base_data
from ..lib.validation.document import validate_document_data


class BaseCustomView(CustomView):
    """ Base Customized View Methods
    """

    def __init__(self, context, request):
        super(BaseCustomView, self).__init__(context, request)

    def _get_data(self):
        """ Get all valid data from (request) POST or PUT.
        """

        return validate_base_data(self, self.request)

    @verify_api_key
    def get_member(self):
        self.wrap=False
        base=self.request.matchdict['base']
        member=self.context.get_member(base, get_base=True)
        response=self.render_to_response(member)

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if self.context.session.is_active:
                self.context.session.close()
        except:
            pass

        return response

    @verify_api_key
    def update_member(self):
        base=self.request.matchdict['base']
        member=self.context.update_member(base, self._get_data())

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if self.context.session.is_active:
                self.context.session.close()
        except:
            pass

        if member is None:
            raise HTTPNotFound()
        else:
            return Response('UPDATED', charset='utf-8', status=200, content_type='')

    @verify_api_key
    def delete_member(self):
        base=self.request.matchdict['base']
        member=self.context.delete_member(base)

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if self.context.session.is_active:
                self.context.session.close()
        except:
            pass

        if member is None:
            raise HTTPNotFound()

        # NOTE: Clear cache! By John Doe
        cache.clear_cache()

        return Response('DELETED', charset='utf-8', status=200, content_type='')

    @verify_api_key
    def get_column(self):
        """ Get column value
        """

        base=self.request.matchdict['base']
        PATH=self.request.matchdict['column'].split('/')
        base=self.context.get_base()
        value=base.asdict
        for path_name in PATH:
            try:
                path_name=int(path_name)
            except:
                pass
            try:
                if isinstance(value, list) and isinstance(path_name, int):
                    value=value[path_name]
                elif path_name in value:
                    value=value[path_name]
                else:
                    value=base.get_struct(path_name).asdict

            except Exception as e:

                # NOTE: Tentar fechar a conexão de qualquer forma!
                # -> Na criação da conexão "coautocommit=True"!
                # By Questor
                try:
                    if self.context.session.is_active:
                        self.context.session.close()
                except:
                    pass

                raise Exception(e)

        value=utils.object2json(value)

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if self.context.session.is_active:
                self.context.session.close()
        except:
            pass

        return Response(value, content_type='application/json')

    def put_column(self):
        basename=self.request.matchdict['base']
        path=self.request.matchdict['column'].split('/')
        json_column=self.request.params['value']
        str_async=self.request.params.get('async', 'false')
        async=str_async.lower() == 'true'
        if async:

            # TODO: get user id! By John Doe
            id_user=0

            user_agent=self.request.user_agent
            user_ip=self.request.client_addr
            task_url=self.context.update_column_async(
                path, 
                json_column, 
                id_user, 
                user_agent, 
                user_ip
            )

            result={
                'task_url': task_url
            }
            response=Response(
                status_code=202, 
                body=utils.object2json(result), 
                content_type='application/json'
            )
            response.content_location=task_url

            # NOTE: Tentar fechar a conexão de qualquer forma!
            # -> Na criação da conexão "coautocommit=True"!
            # By Questor
            try:
                if self.context.session.is_active:
                    self.context.session.close()
            except:
                pass

            return response

        json_current_column=self.context.update_column(path, json_column)

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if self.context.session.is_active:
                self.context.session.close()
        except:
            pass

        return Response(json_current_column, content_type='application/json')
