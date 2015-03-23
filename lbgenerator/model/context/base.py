#!/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging
from . import CustomContextFactory
from ..entities import *
from ..index import Index
from ... import model
from ... import config
from ...lib import utils
from sqlalchemy.util import KeyedTuple

log = logging.getLogger()


class BaseContextFactory(CustomContextFactory):

    """ Base Factory Methods
    """

    entity = LBBase

    def get_next_id(self):
        return model.base_next_id()

    def get_member(self, base):
        self.single_member = True
        member = self.session.query(self.entity)\
            .filter_by(name=base).first()
        return member or None

    def create_member(self, data):

        # Create reg and doc tables
        base_name = data['name']
        base_json = utils.json2object(data['struct'])
        base = model.BASES.set_base(base_json)
        data['struct'] = base.json

        file_table = get_file_table(base_name, config.METADATA)
        doc_table = get_doc_table(base_name, config.METADATA,
            **base.relational_fields)
        file_table.create(config.ENGINE, checkfirst=True)
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

        if member.name != data['name']:
            old_name = 'lb_doc_%s' %(member.name)
            new_name = 'lb_doc_%s' %(data['name'])
            self.session.execute('ALTER TABLE %s RENAME TO %s' %(old_name, new_name))

            old_name = 'lb_file_%s' %(member.name)
            new_name = 'lb_file_%s' %(data['name'])
            self.session.execute('ALTER TABLE %s RENAME TO %s' %(old_name, new_name))

            old_name = 'lb_doc_%s_id_doc_seq' %(member.name)
            new_name = 'lb_doc_%s_id_doc_seq' %(data['name'])
            self.session.execute('ALTER SEQUENCE %s RENAME TO %s' %(old_name, new_name))

            old_name = 'lb_file_%s_id_file_seq' %(member.name)
            new_name = 'lb_file_%s_id_file_seq' %(data['name'])
            self.session.execute('ALTER SEQUENCE %s RENAME TO %s' %(old_name, new_name))

        for name in data:
            setattr(member, name, data[name])
        self.session.commit()

        model.HISTORY.create_member(**{
            'id_base': member.id_base,
            'author': 'Author',
            'date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'name': member.name,
            'structure': utils.json2object(member.struct),
            'status': 'UPDATED'
        })

        self.session.close()

        return member

    def delete_member(self, id):
        member = self.get_member(id)
        if member is None:
            return None

        index = None
        relational_fields = model.BASES.get_base(member.name).relational_fields
        if model.BASES.bases.get(member.name) is not None:
            index = Index(model.BASES.bases[member.name], None)
            del model.BASES.bases[member.name]

        # Delete parallel tables
        file_table = get_file_table(member.name, config.METADATA)
        doc_table = get_doc_table(member.name, config.METADATA, **relational_fields)
        file_table.drop(config.ENGINE, checkfirst=True)
        doc_table.drop(config.ENGINE, checkfirst=True)

        # Delete base
        self.session.delete(member)
        self.session.commit()
        if index:
            index.delete_root()

        model.HISTORY.create_member(**{
            'id_base': member.id_base,
            'author': 'Author',
            'date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'name': member.name,
            'structure': utils.json2object(member.struct),
            'status': 'DELETED'
        })

        self.session.close()
        return member

    def member_to_dict(self, member, fields=None):

        try:
            dict_member = member._asdict()
        except AttributeError as e:
            # Continue parsing
            log.debug("Error parsing as dict!\n%s", e)
            if not isinstance(member, KeyedTuple):
                member = self.member2KeyedTuple(member)

        dict_member = utils.json2object(member._asdict()['struct'])

        fields = getattr(self,'_query', {}).get('select')
        if fields and not '*' in fields:
            return {'metadata':
                {field: dict_member['metadata'][field] for field in fields}
            }

        return dict_member
