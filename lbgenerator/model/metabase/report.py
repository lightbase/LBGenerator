from ...lib import utils
from liblightbase.lbutils.conv import dict2base
import datetime
import traceback

class ReportMetaBase():

    def __init__(self):
        self.structure = {
            "metadata":{
                "id_base": 0,
                "dt_base": datetime.datetime.now(),
                "name": "_report",
                "description": "LightBase's Report Meta Base.",
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
                        "description":"Base ID.",
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
                        "name":"name",
                        "alias":"name",
                        "description":"Report name.",
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
                        "name":"description",
                        "alias":"description",
                        "description":"Report description.",
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
                        "name":"groupby",
                        "alias":"Group by",
                        "description":"Please, provide the field name",
                        "datatype":"Text",
                        "required":False,
                        "multivalued":False,
                        "indices":[
                           "Textual"
                        ]
                    }
                },
                {
                    "field":{
                        "name":"orderby",
                        "alias":"Order by",
                        "description":"Please, provide the field name",
                        "datatype":"Text",
                        "required":False,
                        "multivalued":False,
                        "indices":[
                           "Textual"
                        ]
                    }
                },
                {
                    "field":{
                        "name":"template",
                        "alias":"Layout Type",
                        "description":"Available options: Table, ",
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
                        "name":"pagebreak",
                        "alias":"Page break",
                        "description":"true - block content per page | false - no page break between blocks ",
                        "datatype":"Boolean",
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
                        "description":"Report structure",
                        "datatype":"Json",
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
            literal="name = '_report'"
        )
        bases = base_context.get_collection(query)
        if len(bases) == 0:
            base_context.session = begin_session()
            base_context.create_member(data)

    def create_member(self, **document):

        from ..context.document import DocumentContextFactory
        from ...views.document import DocumentCustomView

        request = utils.FakeRequest(params = {'value': document},
                                    matchdict = {'base': '_report'},
                                    method = 'POST'
                                    )
        def mockfunc(mockparam):
            pass

        request.add_response_callback = mockfunc
        document_context = DocumentContextFactory(request)
        document_view = DocumentCustomView(document_context, request)
        document_view.create_member()
