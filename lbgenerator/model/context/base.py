
from lbgenerator.model.entities import *
from lbgenerator.model.context import CustomContextFactory
from lbgenerator.model import engine
from lbgenerator.model import metadata
from lbgenerator.model import base_context
from lbgenerator.model import reg_hyper_class
from lbgenerator.model import doc_hyper_class

class BaseContextFactory(CustomContextFactory):

    entity = LB_Base

    def create_member(self, data):

        # Create reg and doc tables
        base_name, base_xml = data['nome_base'], data['xml_base']
        custom_cols = base_context.set_base_up(base_name, base_xml)['cc']
        reg_hyper_class(base_name, **custom_cols)
        doc_hyper_class(base_name)
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

        custom_columns = base_context.get_base(member.nome_base)['cc']
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
