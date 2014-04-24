
import datetime
import json
from lbgenerator import model
from lbgenerator.model.entities import *
from lbgenerator.model.context import CustomContextFactory
from lbgenerator.lib import utils
from lbgenerator import config
from lbgenerator.model import base_exists
from lbgenerator.model import reg_hyper_class
from lbgenerator.model import doc_hyper_class
from lbgenerator.model.index import Index
from sqlalchemy.util import KeyedTuple

class BaseContextFactory(CustomContextFactory):

    """ Base Factory Methods
    """

    entity = LB_Base

    def get_member(self, base):
        self.single_member = True
        member = self.session.query(self.entity).filter_by(nome_base = base).first()
        return member or None

    def create_member(self, data):

        if base_exists(data['nome_base']):
            raise Exception('Base "%s" already exists!' % data['nome_base'])
        # Create reg and doc tables
        base_name = data['nome_base']
        base_json = utils.json2object(data['json_base'])
        relational_fields = model.BASES.set_base(base_json).relational_fields

        #reg_hyper_class(base_name, **custom_cols)
        #doc_hyper_class(base_name)
        #metadata.create_all(bind=engine)

        doc_table = get_doc_table(base_name, config.METADATA)
        reg_table = get_reg_table(base_name, config.METADATA, **relational_fields)
        reg_table.create(config.ENGINE, checkfirst=True)
        doc_table.create(config.ENGINE, checkfirst=True)

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

        for name in data:
            setattr(member, name, data[name])
        self.session.commit()

        model.HISTORY.create_member(**{
            'id_base': member.id_base,
            'author': 'Author',
            'date': datetime.datetime.now(),
            'name': member.nome_base,
            'structure': utils.json2object(member.json_base),
            'status': 'UPDATED'
        })

        self.session.close()

        return member

    def delete_member(self, id):
        member = self.get_member(id)
        if member is None:
            return None

        index = None
        relational_fields = model.BASES.get_base(member.nome_base).relational_fields
        if model.BASES.bases.get(member.nome_base) is not None:
            index = Index(model.BASES.bases[member.nome_base], None)
            del model.BASES.bases[member.nome_base]

        # Delete parallel tables
        doc_table = get_doc_table(member.nome_base, config.METADATA)
        reg_table = get_reg_table(member.nome_base, config.METADATA, **relational_fields)
        reg_table.drop(config.ENGINE, checkfirst=True)
        doc_table.drop(config.ENGINE, checkfirst=True)

        # Delete base
        self.session.delete(member)
        self.session.commit()
        if index:
            index.delete_root()

        #metadata.drop_all(bind=engine, tables=[reg_table])
        #metadata.drop_all(bind=engine, tables=[doc_table])

        #self.session.execute('DROP TABLE lb_reg_%s ' % member.nome_base)
        #self.session.execute('DROP TABLE lb_doc_%s ' % member.nome_base)
        #self.session.execute('DROP SEQUENCE lb_reg_%s_id_reg_seq ' % member.nome_base)
        #self.session.execute('DROP SEQUENCE lb_doc_%s_id_doc_seq ' % member.nome_base)

        model.HISTORY.create_member(**{
            'id_base': member.id_base,
            'author': 'Author',
            'date': datetime.datetime.now(),
            'name': member.nome_base,
            'structure': utils.json2object(member.json_base),
            'status': 'DELETED'
        })

        self.session.close()
        return member

    def member_to_dict(self, member, fields=None):
        if not isinstance(member, KeyedTuple):
            member = self.member2KeyedTuple(member)
        dict_member = member._asdict()
        for json_attr in ('json_base', 'reg_model'):
            if json_attr in dict_member:
                dict_member[json_attr] = utils.json2object(dict_member[json_attr])
        return dict_member
