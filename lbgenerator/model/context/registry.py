
from lbgenerator.model.context import CustomContextFactory
from lbgenerator.model.entities import *
import json, inspect, requests, datetime
from lbgenerator.model import base_context
from lbgenerator.model import reg_hyper_class
from lbgenerator.model import doc_hyper_class

class RegContextFactory(CustomContextFactory):

    def __init__(self, request):
        super(RegContextFactory, self).__init__(request)
        custom_columns = base_context.get_base(self.base_name)['cc']
        self.entity = reg_hyper_class(self.base_name, **custom_columns)

    def member_to_dict(self, member, fields=None):
        if fields is None:
            fields = self.default_fields
        d = dict()
        for name in fields:
            attr = getattr(member, name)
            if name == 'json_reg' and attr is not None:
                jdec = json.JSONDecoder()
                try: attr = jdec.raw_decode(attr)[0]
                except Exception as e: raise Exception(e)
            d[name] = attr
        return d

    def delete_member(self, id):
        return super(RegContextFactory, self).delete_member(id, is_reg=True)

    def delete_referenced_docs(self, id_reg):
        """ All docs are relationated with a reg.
            This method deletes all docs referenced by this id_reg
        """
        DocHyperClass = doc_hyper_class(self.base_name)
        ref_docs = self.session.query(DocHyperClass).filter_by(id_reg = id_reg)
        if ref_docs is None: return None
        ref_docs.delete()
