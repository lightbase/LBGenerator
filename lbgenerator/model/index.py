import copy

import requests, datetime
from requests.exceptions import Timeout

from .. import config
from ..lib import utils


class CreatedIndex():
    """ Represents a successfull response when creating an index.
    """
    def __init__(self, created, _index, _type, _id, _version):
        pass

class UpdatedIndex():
    """ Represents a successfull response when updating an index.
    """
    def __init__(self, created, _index, _type, _id, _version):
        pass

class DeletedIndex():
    """ Represents a successfull response when deleting an index.
    """
    def __init__(self, found, _index, _type, _id, _version):
        pass

class DeletedRoot():
    """ Represents a successfull response when deleting root index.
    """
    def __init__(self, acknowledged, ok):
        pass


from .context.txt_idx import TxtIdxContextFactory

class Index(TxtIdxContextFactory):
    """ Handles document index
    """

    def __init__(self, base, get_full_document):
        self.base = base
        self.get_full_document = get_full_document

        self.is_indexable = self.base.metadata.idx_exp
        self.INDEX_URL = self.base.metadata.idx_exp_url
        try:
            if self.base.metadata.idx_exp:
                if not self.base.metadata.idx_exp_url and config.ES_DEF_URL:
                    self.is_indexable = True
                    self.INDEX_URL = config.ES_DEF_URL + "/" + self.base.metadata.name \
                            + "/" + self.base.metadata.name
        except:
            pass

        if self.is_indexable and self.INDEX_URL:
            self._host = self.INDEX_URL.split('/')[2]
            self._index = self.INDEX_URL.split('/')[3]
            self._type = self.INDEX_URL.split('/')[4]

        # Guarda a configuração setada de mapping p/ a base atual!
        self.txt_mapping = self.base.txt_mapping_json

        self.TIMEOUT = config.REQUESTS_TIMEOUT

        '''
        NOTE: Esse parâmetro é para uso final da classe 
        "CacheMaster". Essa classe é por sua vez herdada 
        por "CustomContextFactory"! By Questor
        '''
        self.base_name = "_txt_idx"

    def to_url(self, *args):
        return '/'.join(list(args))

    def is_created(self, msg):
        """ Ensures index is created
        """
        try: CreatedIndex(**msg); return True
        except: return False

    def is_updated(self, msg):
        """ Ensures index is updated
        """
        try: UpdatedIndex(**msg); return True
        except: return False

    def is_deleted(self, msg):
        """ Ensures index is deleted
        """
        # TODO: Essa verificação de erro pela mensagem se limita
        # ao formato do retorno do json. Tá meio tosco! By Questor
        try: DeletedIndex(**msg); return True
        except: return False

    def is_root_deleted(self, msg):
        """ Ensures root index is deleted
        """
        try: DeletedRoot(**msg); return True
        except: return False

    def create_mapping(self):
        """ Cria o mapping indicado p/ a base se não houver.
        """
        if self.txt_mapping is None or self.txt_mapping == "":
            return False

        response_0 = None
        index_url = None
        try:
            index_url = ("http://" + self._host + "/" + self._index + 
                "/" + self._type)
            response_0 = requests.get(index_url + "/_mapping")
            response_0.raise_for_status()
            response_0_json = response_0.json()
        except requests.exceptions.HTTPError as e:
            # NOTE: Normalmente entrará nesse bloco de código 
            # quando o índice não existe! By Questorprint("self.txt_mapping: ")
            return False
        except requests.exceptions.RequestException as e:
            raise Exception("Problem in the mapping provider! " + str(e))
        except Exception as e:
            raise Exception("Mapping operation. Program error! " + str(e))
        
        if response_0.status_code == 200 and not bool(response_0_json):
            response_1 = None
            try:
                response_1 = requests.post(index_url + "/_mapping", 
                    data=self.txt_mapping, 
                    timeout=self.TIMEOUT)
                response_1.raise_for_status()
                response_1_json = response_1.json()
            except requests.exceptions.RequestException as e:
                raise Exception("Problem in the mapping provider! " + str(e))
            except Exception as e:
                raise Exception("Mapping operation. Program error! " + str(e))

            print("response_1_json")
            print(str(response_1_json))
            if (response_1_json is None or
                    response_1_json.get("acknowledged", None) is None or
                    response_1_json.get("acknowledged", None) != True):
                raise Exception("Mapping not created!")

        return True

    def create_index(self):
        """ Cria o índice indicado p/ aquela base se não houver.
        """

        response_0 = None
        index_url = None
        create_index = False
        try:
            index_url = "http://" + self._host + "/" + self._index
            response_0 = requests.get(index_url + "/_settings")
            response_0.raise_for_status()
            response_0_json = response_0.json()
        except requests.exceptions.HTTPError as e:
            create_index = True
        except requests.exceptions.RequestException as e:
            raise Exception("Problem in the index provider! " + str(e))
        except Exception as e:
            raise Exception("Index operation. Program error! " + str(e))

        if (create_index):
                data_value = None
                try:
                    member = self.get_member(self._index)
                except Exception as e:
                    raise Exception(("Failed to get the index setting! "
                        + str(e)))

                # NOTE: Se não houver configuração de indexação "setada" 
                # o sistema vai criar uma padrão! By Questor
                if member is not None:
                    data_value = member.cfg_idx
                else:
                    data_value = '{\
                        "settings":{\
                            "analysis":{\
                                "analyzer":{\
                                    "default":{\
                                        "tokenizer":"standard",\
                                        "filter":[\
                                            "lowercase",\
                                            "asciifolding"\
                                        ]\
                                    }\
                                }\
                            }\
                        }\
                    }'

                response_1 = None
                try:
                    response_1 = requests.post(index_url, 
                        data=data_value, 
                        timeout=self.TIMEOUT)
                    response_1.raise_for_status()
                    response_1_json = response_1.json()
                except requests.exceptions.RequestException as e:
                    raise Exception("Problem in the index provider! " + str(e))
                except Exception as e:
                    raise Exception("Index operation. Program error! " + str(e))

                if (response_1_json is None or
                        response_1_json.get("acknowledged", None) is None or
                        response_1_json.get("acknowledged", None) != True):
                    raise Exception("Index not created!")

    def create(self, data):
        """ Creates index.
        """

        if not self.is_indexable:
            return False, data

        # NOTE: Primeiro verifica o "mapping" e se não houver índice 
        # tenta criar o índice! Se houver índice, tenta criar o 
        # "mapping"! By Questor
        if not self.create_mapping():
            # NOTE: Não havendo índice tenta criá-lo, havendo criado 
            # tenta criar o mapping! By Questor
            self.create_index()
            self.create_mapping()

        # NOTE: Try to index document!
        url = self.to_url(self.INDEX_URL, str(data['id_doc']))
        document = utils.object2json(data['document'], ensure_ascii=True)

        try:
            response = requests.post(url, 
                data=document, 
                timeout=self.TIMEOUT).json()
        except:
            response = None

        if self.is_created(response):
            data['dt_idx'] = datetime.datetime.now()
        else:
            data['dt_idx'] = None
            return False, data

        self.sync_metadata(data) # Syncronize document metadata.
        return True, data

    def update(self, id, data, session):
        """ Updates index 
        """

        if not self.is_indexable:
            return False, data

        # NOTE: Primeiro verifica o "mapping" e se não houver índice 
        # tenta criar o índice! Se houver índice, tenta criar o 
        # "mapping"! By Questor
        if not self.create_mapping():
            # NOTE: Não havendo índice tenta criá-lo, havendo criado 
            # tenta criar o mapping! By Questor
            self.create_index()
            self.create_mapping()

        document_copy = copy.deepcopy(data['document'])

        # Get full document
        full_document = self.get_full_document(document_copy, session)

        # IMPORTANT: This time we dont have ensure_ascii=False
        document = utils.object2json(full_document, ensure_ascii=True)

        url = self.to_url(self.INDEX_URL, str(data['id_doc']))

        try:
            response = requests.put(url,
                data=document,
                timeout=self.TIMEOUT).json()
        except:
            response = None

        if self.is_updated(response):
            data['dt_idx'] = datetime.datetime.now()
        else:
            data['dt_idx'] = None

        self.sync_metadata(data) # Syncronize document metadata.
        return True, data

    def delete(self, id):
        """ Deletes index 
        """
        if not self.is_indexable:
            # index does not exist, error = false
            return False, None

        '''
        TODO: Analisei o comportamento da operação delete e 
        verifiquei que o LBG cria índice e mapping (ES) quando 
        submete delete (verbo DELETE usando a biblioteca "requests" 
        conforme faz com as demais operações) quando não há os 
        mesmos criados. Achei isso conceitualmente errado 
        (aparentemente esse é um comportamento padrão do ES), p/ 
        não dizer esquizito. Ou seja, "eu crio um índice e um 
        mapping na sua operação delete se não houver os mesmos, 
        mesmo que obviamente sob essas condições o registro não 
        exista.". P/ evitar que índices e mappings sejam criados 
        com configurações erradas adotei p/ a operação delete as 
        mesmas ações que p/ as demais operações! Não seria bom 
        rever isso de alguma forma? By Questor
        '''

        # NOTE: Primeiro verifica o "mapping" e se não houver índice 
        # tenta criar o índice! Se houver índice, tenta criar o 
        # "mapping"! By Questor
        if not self.create_mapping():
            # NOTE: Não havendo índice tenta criá-lo, havendo criado 
            # tenta criar o mapping! By Questor
            self.create_index()
            self.create_mapping()

        url = self.to_url(self.INDEX_URL, str(id))

        try:
            response = requests.delete(url, timeout=self.TIMEOUT)
        except Exception as e:
            response = None
            msg_error = str(e)
        else:
            msg_error = response.text

        try:
            response = response.json()
        except Exception as e:
            response = None

        if self.is_deleted(response):
            # index is deleted, error = false 
            return False, None
        else:
            # index is not deleted, error = true 
            data = dict(
                base = self.base.metadata.name,
                id_doc = id,
                dt_error = datetime.datetime.now(),
                msg_error = msg_error)

            return True, data

    def delete_root(self):
        """ Deletes root type
        """
        try: response = requests.delete(self.INDEX_URL, timeout=self.TIMEOUT).json()
        except : response = None

        if self.is_root_deleted(response):
            response = True
        else:
            response = False
        return response

    def sync_metadata(self, data):
        data['document']['_metadata']['dt_idx'] = data\
            .get('dt_idx', None)
