from ...lib import utils
from liblightbase.lbutils.conv import dict2base
import datetime
import traceback

class SearchMetaBase():

    def __init__(self):
        self.structure = {
            "metadata":{
                "id_base": 0,
                "dt_base": datetime.datetime.now(),
                "name":"_search",
                "description":"LightBase's Search Meta Base.",
                "password":"3Ax!vj6gV#DEtR",
                "color":"#000000",
                "idx_exp_url":"",
                "idx_exp_time": 0,
                "file_ext_time": 0,
                "file_ext": False,
                "idx_exp": False
            },
            "content":[
                {
                    "field":{
                        "name":"id_base",
                        "datatype":"Integer",
                        "required": True,
                        "alias":"id_base",
                        "multivalued": False,
                        "indices":[
                            "Textual"
                        ],
                        "description":"Base ID. Identifies the base from which the search was generated."
                    }
                },
                {
                    "field":{
                        "name":"author",
                        "datatype":"Text",
                        "required": True,
                        "alias":"author",
                        "multivalued": False,
                        "indices":[
                            "Textual"
                        ],
                        "description":"Event Author. Contains the id of the author, user, who created the search."
                    }
                },
                {
                    "field":{
                        "name":"name",
                        "datatype":"Text",
                        "required": True,
                        "alias":"Name",
                        "multivalued": False,
                        "indices":[
                            "Textual"
                        ],
                        "description":"Search name. It is a name that identifies the search."
                    }
                },
                {
                    "field":{
                        "name":"type",
                        "datatype":"Text",
                        "required": True,
                        "alias":"Type",
                        "multivalued": False,
                        "indices":[
                            "Textual"
                        ],
                        "description":"Type search. Identifies what type of search. Initially there are 3 types, general, direct and advanced."
                    }
                },
                {
                    "field":{
                        "name":"description",
                        "datatype":"Text",
                        "required": True,
                        "alias":"description",
                        "multivalued": False,
                        "indices":[
                            "Textual"
                        ],
                        "description":"Search description. Explanatory or complementary description to help identify the search."
                    }
                },
                {
                    "field":{
                        "name":"structure",
                        "datatype":"Json",
                        "required": True,
                        "alias":"structure",
                        "multivalued": False,
                        "indices":[
                            "Textual"
                        ],
                        "description":"Search structure. Contains the settings for each search field."
                    }
                }
            ]
        }


    def create_base(self, begin_session):

        from ..context.base import BaseContextFactory
        base = dict2base(self.structure)

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
            literal="name = '_search'"
        )
        bases = base_context.get_collection(query)
        if len(bases) == 0:
            base_context.session = begin_session()
            base_context.create_member(data)

    def create_member(self, **document):

        from ..context.document import DocumentContextFactory
        from ...views.document import DocumentCustomView

        request = utils.FakeRequest(params = {'value': document},
                                    matchdict = {'base': '_search'},
                                    method = 'POST'
                                    )
        def mockfunc(mockparam):
            pass

        request.add_response_callback = mockfunc
        document_context = DocumentContextFactory(request)
        document_view = DocumentCustomView(document_context, request)
        document_view.create_member()
