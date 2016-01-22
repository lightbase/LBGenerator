import json
import datetime

from .. import utils


def validate_txt_idx_data(self, request):
    """ Controla a validação da entrada de dados para a rota 
    "_txt_idx"!
    """

    params, method = utils.split_request(request)

    valid_fields = (
        'cfg_idx_txt'
        )

    data = utils.filter_params(params, valid_fields)

    # NOTE: Valida o json enviado no parâmetro "cfg_idx_txt"! 
    # By Questor
    try:
        if method == 'POST':
            data_adjusted = vldt_n_treat_cfg_idx_txt(self, data, method)
        elif method == 'PUT':
            data_adjusted = vldt_n_treat_cfg_idx_txt(self, data, method)
    except Exception as e:
        raise LbException(
            "Failed to use json contained in \"cfg_idx_txt\" parameter!", 
            str(e))

    return data_adjusted

def vldt_n_treat_cfg_idx_txt(self, data, method):
    """ Trata a entrada de dados para a rota "_txt_idx" conforme o 
    verbo usado!
    """

    if not 'cfg_idx_txt' in data:
        raise Exception("Parameter 'cfg_idx_txt' not found in request!")

    data_adjusted = utils.json2object(data['cfg_idx_txt'])

    if method == 'POST':

        '''
        NOTE: Na criação do registro sobreescreve os parâmetros do json 
        abaixo se foram enviados na criação ou seta se não foram 
        enviados! By Questor
        '''
        data_adjusted['struct'] = utils.object2json(data_adjusted)
        data_adjusted['cfg_idx'] = utils.object2json(data_adjusted["cfg_idx"])
        data_adjusted['dt_crt_idx'] = datetime.datetime.now()
        data_adjusted['dt_upt_idx'] = datetime.datetime.now()
        data_adjusted['actv_idx'] = True

    elif method == 'PUT':

        '''
        NOTE: Evita que o usuário sobrescreva a data de criação, se for
        enviado! By Questor
        '''
        try:
            delattr(data_adjusted, "dt_crt_idx")
        except:
            pass

        data_adjusted['struct'] = utils.object2json(data_adjusted)
        data_adjusted['cfg_idx'] = utils.object2json(data_adjusted["cfg_idx"])
        data_adjusted['dt_upt_idx'] = datetime.datetime.now()
        pass

    return data_adjusted