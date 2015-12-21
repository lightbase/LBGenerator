from ...lib import utils
from liblightbase.lbutils.conv import dict2base
import datetime
import traceback

class HistoryMetaBase():

    def __init__(self):
        self.structure = {
            "metadata":{
                "id_base": 0,
                "dt_base": datetime.datetime.now(),
                "name": "_history",
                "description": "LightBase's History Meta Base.",
                "password": "3Ax!vj6gV#DEtR",
                "color": "#000000",
                "idx_exp_url": "",
                "idx_exp_time": 0,
                "file_ext_time": 0,
                "file_ext": False,
                "idx_exp": False
            },
            "content":[
                {
                    "field":{
                        "name":"id_base",
                        "alias":"id_base",
                        "description":"Base old ID.",
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
                        "name":"author",
                        "alias":"author",
                        "description":"Event Author.",
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
                        "name":"date",
                        "alias":"date",
                        "description":"Event Date.",
                        "datatype":"DateTime",
                        "required":True,
                        "multivalued":False,
                        "indices":[
                            "Textual"
                        ]
                    }
                },
                {
                    "field":{
                        "name":"name",
                        "alias":"name",
                        "description":"Base old name.",
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
                        "name":"structure",
                        "alias":"structure",
                        "description":"Base old structure",
                        "datatype":"Json",
                        "required":True,
                        "multivalued":False,
                        "indices":[
                           "Textual"
                        ]
                    }
                },
                {
                    "field":{
                        "name":"status",
                        "alias":"status",
                        "description":"Base status",
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

    def create_base(self, begin_session):

        from ..context.base import BaseContextFactory
        base = dict2base(self.structure)


        print(str(base))
        print(str(dir(base)))


        data = dict(
            name = base.metadata.name,
            struct = base.json,
            dt_base = datetime.datetime.now(),
            idx_exp = base.metadata.idx_exp,
            idx_exp_url = base.metadata.idx_exp_url,
            idx_exp_time= base.metadata.idx_exp_time,
            file_ext = base.metadata.file_ext,
            file_ext_time = base.metadata.file_ext_time,
            txt_mapping = base.txt_mapping_json
        )

        request = utils.FakeRequest(method = 'POST')
        base_context = BaseContextFactory(request)
        query = dict(
            select=['id_base'],
            literal="name = '_history'"
        )
        bases = base_context.get_collection(query)
        if len(bases) == 0:
            base_context.session = begin_session()
            base_context.create_member(data)

    def create_member(self, **document):

        from ..context.document import DocumentContextFactory
        from ...views.document import DocumentCustomView

        request = utils.FakeRequest(params = {'value': document},
                                    matchdict = {'base': '_history'},
                                    method = 'POST'
                                    )
        def mockfunc(mockparam):
            pass

        request.add_response_callback = mockfunc
        document_context = DocumentContextFactory(request)
        document_view = DocumentCustomView(document_context, request)
        document_view.create_member()
