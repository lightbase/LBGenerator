from ...lib import utils
from liblightbase.lbbase import genesis
import datetime
import traceback

class UserMetaBase():

    def __init__(self):
        self.structure = {
            "metadata":{
                "id_base":0,
                "dt_base": datetime.datetime.now(),
                "name":"_user",
                "description":"LightBase's Users Meta Base.",
                "password":"3Ax!vj6gV#DEtR",
                "color":"#000000",
                "idx_exp_url": "",
                "idx_exp_time": 0,
                "file_ext_time": 0,
                "file_ext": False,
                "idx_exp": False

            },
            "content":[
                {
                    "field":{
                        "name":"id_user",
                        "alias":"id",
                        "description":"LightBase's uses ID",
                        "datatype":"Integer",
                        "required":True,
                        "multivalued":False,
                        "indices":[
                           "Textual"
                        ]
                    }
                },
                {
                    "field":{
                        "name":"name_user",
                        "alias":"name",
                        "description":"User's name",
                        "datatype":"Text",
                        "required":True,
                        "multivalued":False,
                        "indices":[
                           "Textual"
                        ]
                    }
                },
                {
                    "field":{
                        "name":"email_user",
                        "alias":"email",
                        "description":"User's mail",
                        "datatype":"Text",
                        "required":True,
                        "multivalued":False,
                        "indices":[
                            "Textual"
                        ]
                    }
                },
                {
                    "field":{
                        "name":"passwd_user",
                        "alias":"passwd",
                        "description":"User's password",
                        "datatype":"Password",
                        # "datatype":"Text",
                        "required":True,
                        "multivalued":False,
                        "indices":[
                           "Textual"
                        ]
                    }
                },
                {
                    "group":{
                        "metadata":{
                            "name":"bases_user",
                            "alias":"bases",
                            "description":"List of bases that the user can access and what kind of access it is",
                            "multivalued":True
                        },
                        "content":[
                            {
                                "field":{
                                    "name":"name_base",
                                    "alias":"name_base",
                                    "description":"Name of the base the user can access",
                                    "datatype":"Text",
                                    "required":True,
                                    "multivalued":False,
                                    "indices":[
                                        "Textual"
                                    ]
                                }
                            },
                            {
                                "field":{
                                    "name":"access_type",
                                    "alias":"access_type",
                                    "description":"Type of access the user has",
                                    "datatype":"Text",
                                    "required":True,
                                    "multivalued":False,
                                    "indices":[
                                        "Textual"
                                    ]
                                }
                            }
                        ]
                    }
                },
                {
                    "field":{
                        "name":"creation_date_user",
                        "alias":"creation_date",
                        "description":"Date the user account was created",
                        "datatype":"Date",
                        "required":True,
                        "multivalued":False,
                        "indices":[
                           "Textual"
                        ]
                    }
                },
                {
                    "field":{
                        "name":"status_user",
                        "alias":"status",
                        "description":"Check if the user is activer or not",
                        "datatype":"Boolean",
                        "required":True,
                        "multivalued":False,
                        "indices":[
                           "Textual"
                        ]
                    }
                }
            ]
        }


    def create_base(self, begin_session):

        from ..context.base import BaseContextFactory
        base = genesis.json_to_base(self.structure)

        data = dict(
            name = base.metadata.name,
            struct = base.json,
            dt_base = datetime.datetime.now(),
            idx_exp = base.metadata.idx_exp,
            idx_exp_url = base.metadata.idx_exp_url,
            idx_exp_time= base.metadata.idx_exp_time,
            file_ext = base.metadata.file_ext,
            file_ext_time = base.metadata.file_ext_time
        )
        request = utils.FakeRequest(method = 'POST')
        base_context = BaseContextFactory(request)
        query = dict(
            select=['id_base'],
            literal="name = '_user'"
        )
        bases = base_context.get_collection(query)
        if len(bases) == 0:
            base_context.session = begin_session()
            base_context.create_member(data)

    def create_member(self, **document):

        from .context.document import DocumentContextFactory

        request = utils.FakeRequest(matchdict = {'base': '_user'})
        document_context = DocumentContextFactory(request)
        id_reg = document_context.entity.next_id()
        now = datetime.datetime.now()
        document['_metadata'] = {
            "dt_reg": now,
            "id_reg": id_reg,
            "dt_index_tex": None,
            "dt_last_up": now,
            "dt_reg_del": None
        }
        try:
            document_context.create_member({
                'id_reg': id_reg,
                'json_reg': document,
                'dt_reg': now,
                'dt_last_up': now,
                '__cfiles__':[]
            })
        except Exception as e:
            print('ERROR: could not create a new user. id: %s, json: %s, error_msg: %s'
                %(id_reg, document, traceback.format_exc()))
