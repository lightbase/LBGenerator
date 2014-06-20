

class DocsContextFactory():

    """ Document Factory Methods.
    """

    def __init__(self, request):
        self.request = request

#Criando, alterando, deletando e recuperando bases.

    @property
    def get_bases(self):
        return {
            "nickname": "get_bases",
            "method": "GET",
            "summary": "Recuperar Bases",
            "notes": """Retorna uma lista de estruturas de bases existentes, de 
            acordo com a pesquisa fornecida.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "$$",
                    "paramType": "body",
                    "required": False,
                    "type": "JSON",
                    "allowMultiple": False,
                    "description": "JSON de pesquisa"
                }
            ],
        }

    @property
    def create_base(self):
        return {
            "nickname": "create_base",
            "method": "POST",
            "summary": "Criar Base",
            "notes": """Cria uma base, de acordo com a estrutura fornecida. 
            Retorna o id da base em caso de sucesso.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "struct",
                    "paramType": "body",
                    "required": True,
                    "type": "JSON",
                    "allowMultiple": False,
                    "description": "Estrutura da Base"
                }
            ],
        }

    @property
    def get_base(self):
        return {
            "nickname": "get_base",
            "method": "GET",
            "summary": "Recuperar estrutura da base.",
            "notes": "Retorna a estrutura da base.",
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                    "description": "Nome da base"
                }
            ],
        }

    @property
    def update_base(self):
        return {
            "nickname": "put_base",
            "method": "PUT",
            "summary": "Alterar estrutura da base.",
            "notes": """Altera a estrutura da base, de acordo com a estrutura 
            fornecida. Retorna <b>UPDATED</b> em caso de sucesso.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "struct",
                    "paramType": "body",
                    "required": True,
                    "type": "JSON",
                    "allowMultiple": False,
                    "description": "Estrutura da Base"
                }
            ],
        }

    @property
    def delete_base(self):
        return {
            "nickname": "put_base",
            "method": "DELETE",
            "summary": "Deletar Base.",
            "notes": """Deleta a base. Retorna <b>DELETED</b> em caso de
            sucesso.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters":[
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
            ],
        }

#Criando, alterando, deletando e recuperando documentos.

    @property
    def create_document(self):
        return {
            "nickname": "create_document",
            "method": "POST",
            "summary": "Inserir documento.",
            "notes": """Insere um novo documento na base. Retorna o id do 
            documento em caso de sucesso.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters":[
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
            ],
        }

    @property
    def get_document(self):
        return {
            "nickname": "get_document",
            "method": "GET",
            "summary": "Recuperar documento",
            "notes": """ Retorna o documento da {base} representado pelo
            {id}.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters":[
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "id_doc",
                    "description": "ID do documento",
                    "paramType": "path",
                    "required": True,
                    "type": "integer",
                    "format": "int64",
                    "allowMultiple": False,
                },
            ],
        }

    @property
    def update_document(self):
        return {
            "nickname": "update_document",
            "method": "PUT",
            "summary": "Alterar documento",
            "notes": """Altera o documento da {base} representado pelo {id} para
             o novo documento. Retorna <b>UPDATED</b> em caso de sucesso. """,
            #"type": "Pet",
            "authorizations": {},
            "parameters":[
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "id_doc",
                    "description": "ID do documento",
                    "paramType": "path",
                    "required": True,
                    "type": "integer",
                    "format": "int64",
                    "allowMultiple": False,
                },
            ],
        }

    @property
    def delete_document(self):
        return {
            "nickname": "delete_document",
            "method": "DELETE",
            "summary": "Deletar documento.",
            "notes": """Remove o documento da {base} representado pelo {id_doc}. 
            Retorna <b>DELETED</b> em caso de sucesso.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters":[
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "id_doc",
                    "description": "ID do documento",
                    "paramType": "path",
                    "required": True,
                    "type": "integer",
                    "format": "int64",
                    "allowMultiple": False,
                },
            ],
        }
#Criando, alterando, deletando e recuperando arquivos.

    @property
    def get_file_collection(self):
        return {
            "nickname": "get_file_collection",
            "method": "GET",
            "summary": "Recuperar arquivos",
            "notes": """Retorna uma lista de arquivos existentes, de acordo 
            com a pesquisa fornecida.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "$$",
                    "description": "JSON de pesquisa",
                    "paramType": "body",
                    "required": False,
                    "type": "JSON",
                    "allowMultiple": False,
                }
            ]
        }

    @property
    def get_file(self):
        return {
            "nickname": "get_file_id",
            "method": "GET",
            "summary": "Recuperar arquivo",
            "notes": """Retorna os atributos do arquivo da {base} representado
             pelo {id_file}. """,
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "id_file",
                    "description": "ID do arquivo",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                }
            ]
        }

    @property
    def get_file_path(self):
        return {
            "nickname": "get_file_path",
            "method": "GET",
            "summary": "Recuperar atributo do arquivo",
            "notes": """ """,
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "disposition",
                    "description": """Forma com que o arquivo será enviando.
                    Possíveis valores são:<br/>
                    - <b>attachment</b>: Usado para baixar o arquivo 
                    automaticamente.<br/>
                    - <b>inline</b>: Usado para apresentar o arquivo no navegador.""",
                    "paramType": "body",
                    "required": False,
                    "type": "string",
                    "allowMultiple": False,
                }
            ]
        }

    @property
    def create_file(self):
        return {
            "nickname": "create_file",
            "method": "POST",
            "summary": "Upload de arquivo",
            "notes": """Esta URI serve para upload de arquivos. Se no corpo da
            requisição estiver presente um arquivo, será gerada uma chave, que
            somente poderá ser usada para inserir documentos na {base}.
            Retorna uma chave (UUID) em caso de sucesso.""",
            #"type": "Pet",
            "consumes": [
                "multipart/form-data"
            ],
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "file",
                    "description": """Arquivo binário a ser feito o upload.""",
                    "paramType": "body",
                    "required": True,
                    "type": "File",
                    "allowMultiple": False,
                }
            ]
        }

#Criando, alterando, deletando e recuperando nós dos documentos.

    @property
    def get_document_path(self):
        return {
            "nickname": "get_document_path",
            "method": "GET",
            "summary": "Busca parte do documento",
            "notes": """Retorna parte do documento da {base} representado pelo 
            {id} e pelo caminho do path """,
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "id_doc",
                    "description": "ID do documento",
                    "paramType": "path",
                    "required": True,
                    "type": "integer",
                    "allowMultiple": False,
                },
                {
                    "name": "path",
                    "description": "path em que o dado se encontra",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                }
            ]
        }


    @property
    def post_document_path(self):
        return {
            "nickname": "post_document_path",
            "method": "POST",
            "summary": "insere um objeto JSON no documento",
            "notes": """Insere um objeto JSON no documento da {base} representado pelo 
            {id} e pelo caminho do path
            Funciona apenas para Campos ou Grupos multi valorados.
            Retorna o último índice da lista em que o objeto foi inserido.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "id_doc",
                    "description": "ID do documento",
                    "paramType": "path",
                    "required": True,
                    "type": "integer",
                    "allowMultiple": False,
                },
                {
                    "name": "path",
                    "description": "path em que o dado se encontra",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "value",
                    "paramType": "body",
                    "required": True,
                    "type": "JSON",
                    "allowMultiple": False,
                    "description": "Objeto JSON a ser inserido no caminho representado pelo path"
                }
            ],
        }

    @property
    def put_document_path(self):
        return {
            "nickname": "put_document_path",
            "method": "PUT",
            "summary": "Altera um objeto JSON no documento",
            "notes": """Altera um objeto JSON no documento da {base} representado pelo {id} 
            e pelo caminho do path,
            Retorna “UPDATED” em caso de sucesso.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "id_doc",
                    "description": "ID do documento",
                    "paramType": "path",
                    "required": True,
                    "type": "integer",
                    "allowMultiple": False,
                },
                {
                    "name": "path",
                    "description": "path em que o dado se encontra",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "value",
                    "paramType": "body",
                    "required": True,
                    "type": "JSON",
                    "allowMultiple": False,
                    "description": "Objeto JSON a ser inserido"
                }
            ],
        }

    @property
    def delete_document_path(self):
        return {
            "nickname": "delete_document_path",
            "method": "DELETE",
            "summary": "Deleta o documento apartir do path",
            "notes": """Remove um objeto JSON no caminho representado pelo path
            do documento representado pelo {id} da {base}.
            Retorna “DELETED” em caso de sucesso.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "id_doc",
                    "description": "ID do documento",
                    "paramType": "path",
                    "required": True,
                    "type": "integer",
                    "allowMultiple": False,
                },
                {
                    "name": "path",
                    "description": "path em que o dado se encontra",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                }
            ]
        }

#Alterando coleção de documentos pelo caminho dos nós.

    @property
    def put_document_colection(self):
        return {
            "nickname": "put_document_colection",
            "method": "PUT",
            "summary": "Altera o path do documento",
            "notes": """Altera o path do documento da {base} retornados pela pesquisa. 
            Retorna um objeto JSON com a contagem de sucesso e falhas.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "$$",
                    "paramType": "body",
                    "required": True,
                    "type": "JSON",
                    "allowMultiple": False,
                    "description": "Objeto JSON a ser inserido"
                },
                {
                    "name": "path",
                    "paramType": "body",
                    "required": True,
                    "type": "JSON",
                    "allowMultiple": False,
                    "description": "caminho do path separado por barra"
                },
                {
                    "name": "value",
                    "paramType": "body",
                    "required": True,
                    "type": "JSON",
                    "allowMultiple": False,
                    "description": "objeto a ser alterado"
                },

            ]
        }
    @property
    def delete_document_colection(self):
        return {
            "nickname": "delete_document_colection",
            "method": "DELETE",
            "summary": "Deleta o path do documento",
            "notes": """Remove os nós dos documentos da {base} retornados pela pesquisa. 
            Retorna um objeto JSON com a contagem de sucesso e falhas.""",
            #"type": "Pet",
            "authorizations": {},
            "parameters": [
                {
                    "name": "base",
                    "description": "Nome da base",
                    "paramType": "path",
                    "required": True,
                    "type": "string",
                    "allowMultiple": False,
                },
                {
                    "name": "$$",
                    "paramType": "body",
                    "required": True,
                    "type": "JSON",
                    "allowMultiple": False,
                    "description": "JSON de busca"
                },
                {
                    "name": "path",
                    "paramType": "body",
                    "required": True,
                    "type": "JSON",
                    "allowMultiple": False,
                    "description": "Path a ser deletado"
                }


            ]
        }

