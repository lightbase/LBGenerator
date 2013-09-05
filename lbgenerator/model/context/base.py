
import datetime
from lbgenerator.model.entities import *
from lbgenerator.model.context import CustomContextFactory
from lbgenerator.lib import utils
from lbgenerator.model import engine
from lbgenerator.model import metadata
from lbgenerator.model import BASES
from lbgenerator.model import _history
from lbgenerator.model import reg_hyper_class
from lbgenerator.model import doc_hyper_class

class BaseContextFactory(CustomContextFactory):

    entity = LB_Base

    def create_member(self, data):

         # Create reg and doc tables
        base_name = data['nome_base']
        base_json = utils.to_json(data['json_base'])
        custom_cols = BASES.set_base_up(base_json).custom_columns
        reg_hyper_class(base_name, **custom_cols)
        doc_hyper_class(base_name)
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
        
        if member.nome_base != data['nome_base']:
            old_name = 'lb_reg_%s' %(member.nome_base)
            new_name = 'lb_reg_%s' %(data['nome_base'])
            self.session.execute('ALTER TABLE %s RENAME TO %s' %(old_name, new_name))

            old_name = 'lb_doc_%s' %(member.nome_base)
            new_name = 'lb_doc_%s' %(data['nome_base'])
            self.session.execute('ALTER TABLE %s RENAME TO %s' %(old_name, new_name))

            old_name = 'lb_reg_%s_id_reg_seq' %(member.nome_base)
            new_name = 'lb_reg_%s_id_reg_seq' %(data['nome_base'])
            self.session.execute('ALTER SEQUENCE %s RENAME TO %s' %(old_name, new_name))

            old_name = 'lb_doc_%s_id_doc_seq' %(member.nome_base)
            new_name = 'lb_doc_%s_id_doc_seq' %(data['nome_base'])
            self.session.execute('ALTER SEQUENCE %s RENAME TO %s' %(old_name, new_name))

        _history.create_member(**{
            'id_base': member.id_base,
            'author': 'Author',
            'date': str(datetime.datetime.now()),
            'name': member.nome_base,
            'structure': member.json_base,
            'status': 'UPDATED'
        })

        for name in data:
            setattr(member, name, data[name])
        self.session.commit()
        self.session.close()
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

        _history.create_member(**{
            'id_base': member.id_base,
            'author': 'Author',
            'date': str(datetime.datetime.now()),
            'name': member.nome_base,
            'structure': member.json_base,
            'status': 'DELETED'
        })

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
