from lbgenerator.lib import utils
from liblightbase.lbbase import genesis
import json
import datetime
import traceback

class HistoryMetaBase():

    def __init__(self):
        self.structure = {
           "metadata":{
                "name": "_history",
                "description": "LightBase's History Meta Base.",
                "password": "password",
                "color": "color",
                "index_url": "",
                "index_time": 0,
                "extract_time": 0,
                "doc_extract": False,
                "index_export": False
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

        from lbgenerator.model.context.base import BaseContextFactory
        base = genesis.json_to_base(self.structure)

        data = dict(
            nome_base = base.name,
            json_base = base.json,
            reg_model = base.reg_model,
            dt_base = str(datetime.datetime.now()),
            password = base.password,
            index_export = base.index_export,
            index_url = base.index_url,
            index_time= base.index_time,
            doc_extract = base.doc_extract,
            extract_time = base.extract_time
        )
        request = utils.FakeRequest(method = 'POST')
        base_context = BaseContextFactory(request)
        query = dict(
            select=['id_base'],
            literal="nome_base = '_history'"
        )
        bases = base_context.get_collection(query)
        if len(bases) == 0:
            base_context.session = begin_session()
            base_context.create_member(data)

    def create_member(self, **registry):

        from lbgenerator.model.context.registry import RegContextFactory

        request = utils.FakeRequest(matchdict = {'base': '_history'})
        reg_context = RegContextFactory(request)
        id_reg = reg_context.entity.next_id()
        now = datetime.datetime.now()
        registry['_metadata'] = {
            "dt_reg": now,
            "id_reg": id_reg,
            "dt_index_tex": None,
            "dt_last_up": now,
            "dt_reg_del": None
        }
        try:
            reg_context.create_member({
                'id_reg': id_reg,
                'json_reg': registry,
                'dt_reg': now,
                'dt_last_up': now,
                '__docs__': {}
            })
        except Exception as e:
            print('ERROR: could not create registry on _history. id: %s, json: %s, error_msg: %s'
                %(id_reg, registry, traceback.format_exc()))






