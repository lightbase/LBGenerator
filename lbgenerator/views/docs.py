from pyramid.response import Response

from ..lib import utils


class DocsCustomView():

    """ Registry Customized View Methods.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def api_docs(self):
        if self.request.path_info == '/api-docs':
            documentation = self._api_docs
        elif self.request.path_info == '/api-docs/base':
            documentation = self._base_docs
        elif self.request.path_info == '/api-docs/doc':
            documentation = self._document_docs
        elif self.request.path_info == '/api-docs/file':
            documentation = self._file_docs
        else:
            pass

        response = Response(utils.object2json(documentation))
        response.headerlist.append(('Access-Control-Allow-Origin',
            'http://petstore.swagger.wordnik.com'))
        return response

    @property
    def _api_docs(self):
        return {
            "apiVersion": "1.0.0",
            "swaggerVersion": "1.2",
            "info": {
                "title": "LightBase REST API",
                "description": """This is a sample server Petstore server.  You can
                find out more about Swagger \n    at <a href=\"http://swagger.wordn
                ik.com\">http://swagger.wordnik.com</a> or on irc.freenode.net, #swa
                gger.  For this sample,\n    you can use the api key \"special-key\"
                to test the authorization filters""",
                "termsOfServiceUrl": "http://helloreverb.com/terms/",
                "contact": "antony.carvalho@.lightbase.com.br",
                "license": "Apache 2.0",
                "licenseUrl": "http://www.apache.org/licenses/LICENSE-2.0.html"
            },
            "apis": [
                {
                    "path": "/base",
                    "description": "Operações das Bases"
                },
                {
                    "path": "/doc",
                    "description": "Operações dos documentos."
                },
                {
                    "path": "/file",
                    "description": "Operações dos arquivos."
                },
            ]
        }

    @property
    def _base_docs(self):
        return {
            "swaggerVersion": "1.2",
            "basePath": self.request.application_url,
            "produces": [
                "application/json",
                "text/plain",
            ],
            "resourcePath": "/base",
            "apiVersion": "1.0.0",
            "apis": [
                {
                    "path": "/",
                    "operations": [
                        self.context.get_bases,
                        self.context.create_base,
                    ],
                },
                {
                    "path": "/{base}",
                    "operations": [
                        self.context.get_base,
                        self.context.update_base,
                        self.context.delete_base,
                    ],
                },
            ],
            "models": self.models
        }

    @property
    def _document_docs(self):
        return {
            "swaggerVersion": "1.2",
            "basePath": self.request.application_url,
            "produces": [
                "application/json",
                "text/plain",
            ],
            "resourcePath": "/doc",
            "apiVersion": "1.0.0",
            "apis": [
                {
                    "path": "/{base}/doc",
                    "operations": [
                        self.context.create_document
                    ],
                },
                {
                    "path": "/{base}/doc/{id_doc}",
                    "operations": [
                        self.context.get_document,
                        self.context.update_document,
                        self.context.delete_document,
                    ],
                },
                {
                    "path": "/{base}/doc/{id_doc}/{path}",
                    "operations": [
                        self.context.get_document_path,
                        self.context.post_document_path,
                        self.context.put_document_path,
                        self.context.delete_document_path,
                    ],

                },
                {
                    "path": "/{base}/reg",
                    "operations": [
                        self.context.put_document_colection,
                        self.context.delete_document_colection,
                    ],
                },

            ],
            "models": self.models
        }

    @property
    def _file_docs(self):
        return {
            "swaggerVersion": "1.2",
            "basePath": self.request.application_url,
            "produces": [
                "application/json",
                "text/plain",
            ],
            "resourcePath": "/file",
            "apiVersion": "1.0.0",
            "apis": [
                {
                    "path": "/{base}/file",
                    "operations": [
                        self.context.get_file_collection,
                        self.context.create_file
                    ],
                },
                {
                    "path": "/{base}/file/{id_file}",
                    "operations": [
                        self.context.get_file,
                    ],
                },
                {
                    "path": "/{base}/file/{id_file}/{path}",
                    "operations": [
                        self.context.get_file_path,
                    ],
                },
            ],
            "models": self.models
        }

    @property
    def models(self):
        return {
            "Pet": {
                "required": [
                    "id",
                    "name"
                ],
                "id": "Pet",
                "properties": {
                    "category": {
                        "$ref": "Category"
                    },
                    "status": {
                        "enum": [
                            "available",
                            "pending",
                            "sold"
                        ],
                        "type": "string",
                        "description": "pet status in the store"
                    },
                    "name": {
                        "type": "string"
                    },
                    "tags": {
                        "items": {
                            "$ref": "Tag"
                        },
                        "type": "array"
                    },
                    "photoUrls": {
                        "items": {
                            "type": "string"
                        },
                        "type": "array"
                    },
                    "id": {
                        "minimum": "0.0",
                        "type": "integer",
                        "description": "unique identifier for the pet",
                        "maximum": "100.0",
                        "format": "int64"
                    }
                }
            },
            "Category": {
                "id": "Category",
                "properties": {
                    "id": {
                        "type": "integer",
                        "format": "int64"
                    },
                    "name": {
                        "type": "string"
                    }
                }
            },
            "Tag": {
                "id": "Tag",
                "properties": {
                    "id": {
                        "type": "integer",
                        "format": "int64"
                    },
                    "name": {
                        "type": "string"
                    }
                }
            }
        }
