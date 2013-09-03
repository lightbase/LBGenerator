
from lbgenerator.model.entities import *
from lbgenerator.model.context import CustomContextFactory
from lbgenerator.lib import utils
from lbgenerator.model import engine
from lbgenerator.model import metadata
from lbgenerator.model import base_context
from lbgenerator.model import reg_hyper_class
from lbgenerator.model import doc_hyper_class

class BaseContextFactory(CustomContextFactory):

    entity = LB_Base

    def create_member(self, data):

        # Create reg and doc tables
        base_json = utils.to_json(data['json_base'])
        base = base_context.set_base_up(base_json)

        data['nome_base'] = base.name
        data['reg_model'] = base.reg_model

        reg_hyper_class(base.name, **base.custom_columns)
        doc_hyper_class(base.name)
        metadata.create_all(bind=engine)

        member = self.entity(**data)
        self.session.add(member)
        self.session.commit()
        self.session.close()
        return member

    def delete_member(self, id):
        member = self.get_member(id, force=True)
        if member is None:
            return None

        custom_columns = base_context.get_base(member.nome_base).custom_columns
        if base_context.bases.get(member.nome_base) is not None:
            del base_context.bases[member.nome_base]

        # Delete parallel tables
        doc_table = get_doc_table(member.nome_base, metadata)
        reg_table = get_reg_table(member.nome_base, metadata, **custom_columns)
        metadata.drop_all(bind=engine, tables=[reg_table])
        metadata.drop_all(bind=engine, tables=[doc_table])

        # Delete base
        self.session.delete(member)
        self.session.commit()
        self.session.close()
        return member
        
    def member_to_dict(self, member, fields=None):
        if fields is None:
            fields = self.default_fields
        dic = dict()
        for name in fields:
            attr = getattr(member, name)
            if name == 'json_base':
                attr = utils.to_json(attr)
            dic[name] = attr
        return dic
