
from lbgenerator.model.entities import *
from lbgenerator.model.context import CustomContextFactory
from lbgenerator.lib import utils
from lbgenerator.model import engine
from lbgenerator.model import metadata
from lbgenerator.model import BASES
from lbgenerator.model import reg_hyper_class
from lbgenerator.model import doc_hyper_class

class BaseContextFactory(CustomContextFactory):

    entity = LB_Base

    def create_member(self, data):

        # Create reg and doc tables
        base_json = utils.to_json(data['json_base'])
        base = BASES.set_base_up(base_json)

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

    def update_member(self, id, data):
        member = self.get_member(id)
        if member is None:
            return None
        
        base_json = utils.to_json(data['json_base'])
        base = BASES.set_base_up(base_json)

        data['nome_base'] = base.name
        data['reg_model'] = base.reg_model
    
        if member.nome_base != base.name:

            old_name = 'lb_reg_%s' % member.nome_base
            new_name = 'lb_reg_%s' % base.name
            self.session.execute('ALTER TABLE %s RENAME TO %s' % (old_name, new_name))

            old_name = 'lb_reg_%s_id_reg_seq' % member.nome_base
            new_name = 'lb_reg_%s_id_reg_seq' % base.name
            self.session.execute('ALTER SEQUENCE %s RENAME TO %s' % (old_name, new_name))

            old_name = 'lb_doc_%s' % member.nome_base
            new_name = 'lb_doc_%s' % base.name
            self.session.execute('ALTER TABLE %s RENAME TO %s' % (old_name, new_name))

            old_name = 'lb_doc_%s_id_doc_seq' % member.nome_base
            new_name = 'lb_doc_%s_id_doc_seq' % base.name
            self.session.execute('ALTER SEQUENCE %s RENAME TO %s' % (old_name, new_name))

        for name in data:
            setattr(member, name, data[name])
        self.session.commit()
        return member

    def delete_member(self, id):
        member = self.get_member(id, force=True)
        if member is None:
            return None

        custom_columns = BASES.get_base(member.nome_base).custom_columns
        if BASES.bases.get(member.nome_base) is not None:
            del BASES.bases[member.nome_base]

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
