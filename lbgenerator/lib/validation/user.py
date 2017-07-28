import datetime

from .. import utils
from ..validation import document


def validate_user_data(cls, request, id=None):
    params, method=utils.split_request(request)
    if method == 'GET': return None
    valid_fields=(
        'id_user', 
        'name_user', 
        'email_user', 
        'passwd_user', 
        'api_key'
    )
    data=utils.filter_params(params, valid_fields)
    if method == 'POST':
        return validate_post_data(cls, data)
    elif method == 'PUT':
        if not id: id=int(request.matchdict['id'])
        return validate_put_data(cls, data, id)

def validate_post_data(cls, data):

    # TODO: Centralizar lógica de validação de params! By John Doe
    if not 'id_user' in data:
        raise Exception("param 'id_user' not found in request")

    if not 'name_user' in data:
        raise Exception("param 'name_user' not found in request")

    if not 'email_user' in data:
        raise Exception("param 'email_user' not found in request")

    if not 'passwd_user' in data:
        raise Exception("param 'passwd_user' not found in request")
 
    today=datetime.date.today()
    data['creation_date_user']=today.strftime("%d/%m/%Y")
    data['status_user']=True

    # NOTE: Removi o campo groups user por enquanto. Para voltar, basta
    # descomentar as linhas abaixo e alterar a estrutura da base _user
    # adicionando o campo! By Landim

    # TODO: Configurar grupo padrão para criação de usuário! By John Doe

    newData=dict()
    newData['value']=data

    # TODO: Dependente da camada de repositório Lightbase! By John Doe

    return document.validate_post_data(cls, newData)

def validate_put_data(cls, data, id):
    return data
