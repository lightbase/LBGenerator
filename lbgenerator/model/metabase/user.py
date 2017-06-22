import datetime
import traceback

from liblightbase.lbutils.conv import dict2base

from ...lib import utils


class UserMetaBase():

    def __init__(self):
        self.structure={
            "content": [{
                "field": {
                    "name": "id_user",
                    "datatype": "Text",
                    "required": True,
                    "alias": "id",
                    "multivalued": False,
                    "indices": ["Textual", "Ordenado"],
                    "description": "LightBase\'s uses ID"
                }
            }, {
                "field": {
                    "name": "api_key",
                    "datatype": "Text",
                    "required": False,
                    "alias": "api_key",
                    "multivalued": False,
                    "indices": ["Textual", "Ordenado"],
                    "description": "LightBase\'s api key"
                }
            }, {
                "field": {
                    "name": "name_user",
                    "datatype": "Text",
                    "required": True,
                    "alias": "name",
                    "multivalued": False,
                    "indices": ["Textual", "Ordenado"],
                    "description": "User\'s name"
                }
            }, {
                "field": {
                    "name": "email_user",
                    "datatype": "Text",
                    "required": True,
                    "alias": "email",
                    "multivalued": False,
                    "indices": ["Textual"],
                    "description": "User\'s mail"
                }
            }, {
                "field": {
                    "name": "passwd_user",
                    "datatype": "Text",
                    "required": True,
                    "alias": "passwd",
                    "multivalued": False,
                    "indices": ["Textual"],
                    "description": "User\'s password"
                }
            }, {
                "group": {
                    "content": [{
                        "field": {
                            "name": "name_base",
                            "datatype": "Text",
                            "required": True,
                            "alias": "name_base",
                            "multivalued": False,
                            "indices": ["Textual"],
                            "description": "Name of the base the user can " +\
                                    "access"
                        }
                    }, {
                        "field": {
                            "name": "access_groups",
                            "datatype": "Text",
                            "required": True,
                            "alias": "access_groups",
                            "multivalued": True,
                            "indices": ["Textual", "Ordenado"],
                            "description": "Type of access the user has"
                        }
                    }],
                    "metadata": {
                        "multivalued": True,
                        "alias": "bases",
                        "name": "bases_user",
                        "description": "List of bases that the user can " +\
                                "access and what kind of access it is"
                    }
                }
            }, {
                "field": {
                    "name": "creation_date_user",
                    "datatype": "Date",
                    "required": True,
                    "alias": "creation_date",
                    "multivalued": False,
                    "indices": ["Textual"],
                    "description": "Date the user account was created"
                }
            }, {
                "field": {
                    "name": "status_user",
                    "datatype": "Boolean",
                    "required": True,
                    "alias": "status",
                    "multivalued": False,
                    "indices": ["Textual"],
                    "description": "Check if the user is activer or not"
                }
            }, {
                "field": {
                    "name": "groups_user",
                    "datatype": "Text",
                    "required": False,
                    "alias": "groups_user",
                    "multivalued": True,
                    "indices": ["Textual", "Ordenado"],
                    "description": "Groups that user has access"
                }
            }],
            "metadata": {
                "idx_exp": False,
                "description": "LightBase\'s Users Meta Base.",
                "color": "#000000",
                "file_ext_time": 0,
                "dt_base": datetime.datetime.now(),
                "idx_exp_url": "",
                "file_ext": False,
                "password": "3Ax!vj6gV#DEtR",
                "id_base": 0,
                "name": "_user",
                "idx_exp_time": 0,
                "model": {
                    "name_user": "Text",
                    "groups_user": ["Text"],
                    "status_user": "Boolean",
                    "bases_user": [{
                        "access_groups": ["Text"],
                        "name_base": "Text"
                    }],
                    "id_user": "Text",
                    "creation_date_user": "Date",
                    "api_key": "Text",
                    "email_user": "Text",
                    "passwd_user": "Text"
                }
            }
        }

    def create_base(self, begin_session):
        try:
            from ..context.base import BaseContextFactory

            base=dict2base(self.structure)
            data=dict(
                name=base.metadata.name,
                struct=base.json,
                dt_base=datetime.datetime.now(),
                idx_exp=base.metadata.idx_exp,
                idx_exp_url=base.metadata.idx_exp_url,
                idx_exp_time=base.metadata.idx_exp_time,
                file_ext=base.metadata.file_ext,
                file_ext_time=base.metadata.file_ext_time
            )
            request=utils.FakeRequest(method='POST')
            base_context=BaseContextFactory(request)
            query=dict(
                select=['id_base'],
                literal="name = '_user'"
            )
            bases=base_context.get_collection(query)
            if len(bases) == 0:
                base_context.session=begin_session()
                base_context.create_member(data)
        except Exception as e:

            # TODO: Tratar erro! By Questor
            pass

    def create_member(self, **document):
        from .context.document import DocumentContextFactory

        request=utils.FakeRequest(matchdict={'base': '_user'})
        document_context=DocumentContextFactory(request)
        id_reg=document_context.entity.next_id()
        now=datetime.datetime.now()
        document['_metadata']={
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
            print('ERROR: could not create a new user. id: %s, json: %s, ' +\
                    'error_msg: %s' % (
                        id_reg, 
                        document, 
                        traceback.format_exc()
                    )
            )
