from lbgenerator.model.context.registry import RegContextFactory
from lbgenerator.lib import utils
from liblightbase.lbbase import genesis
import json
import datetime
from sqlalchemy import Sequence

class HistoryMetaBase(object):

    def __init__(self):
        self.seq = Sequence('lb_doc__history_id_doc_seq')
        self.structure = {
           "metadata":{
                "name":"_history",
                "description":"LightBase's History Meta Base.",
                "password": "password",
                "color": "color",
                "index_url":"",
                "index_time":"0",
                "extract_time":"0",
                "doc_extract":False,
                "index_export":False
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
            nome_base = self.structure['metadata']['name'],
            json_base = json.dumps(self.structure),
            reg_model = str(base.schema.schema),
            dt_base = str(datetime.datetime.now())
        )
        request = utils.FakeRequest(method = 'POST')
        base_context = BaseContextFactory(request)
        bases = base_context.get_collection(
            select=['id_base'],
            literal="nome_base = '_history'"
        )
        if len(bases) == 0:
            base_context.session = begin_session()
            base_context.create_member(data)

    def create_member(self, **registry):

        request = utils.FakeRequest(matchdict = {'base': '_history'})
        reg_context = RegContextFactory(request)
        id_reg = reg_context.entity.next_id()
        registry['id_reg'] = id_reg
        json_reg = json.dumps(registry, ensure_ascii=False)
        try:
            reg_context.create_member({
                'id_reg': id_reg,
                'json_reg': json_reg,
                'dt_reg': datetime.datetime.now()
            })
        except:
            print('ERROR: could not create registry on _history. id: %s, json: %s' %(id_reg, json_reg))






