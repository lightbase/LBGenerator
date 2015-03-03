#!/bin/env python
# -*- coding: utf-8 -*-
import sqlalchemy
import logging
from ... import model
from ...lib import utils
from sqlalchemy import asc, desc
from pyramid.security import Deny
from pyramid.security import Allow
from ...lib.query import JsonQuery
from ...model import begin_session
from pyramid.security import Everyone
from sqlalchemy.util import KeyedTuple
from pyramid.compat import string_types
from sqlalchemy.sql.expression import func
from pyramid.security import Authenticated
from pyramid.security import ALL_PERMISSIONS
from pyramid_restler.model import SQLAlchemyORMContext


log = logging.getLogger()

class CustomContextFactory(SQLAlchemyORMContext):

    """ Default Factory Methods
    """

    json_encoder = utils.DocumentJSONEncoder

    __acl__ = [
        (Allow, 'group:viewers', 'view'),
        (Allow, 'group:creators', 'create'),
        (Allow, 'group:editors', 'edit'),
        (Allow, 'group:deleters', 'delete'),
        (Allow, Authenticated, ALL_PERMISSIONS),
        (Deny, Everyone, ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request
        self.base_name = self.request.matchdict.get('base')

    def session_factory(self):
        """ Connect to database and begin transaction
        """
        if getattr(self, 'overwrite_session', False) is True:
            return self.__session__
        return begin_session()

    def get_base(self):
        """ Return Base object
        """
        return model.BASES.get_base(self.base_name)

    def set_base(self, base_json):
        """ Set Base object
        """
        return model.BASES.set_base(base_json)

    def get_member(self, id, close_sess=True):
        self.single_member = True
        q = self.session.query(self.entity)
        member = q.get(id)
        if close_sess:
            self.session.close()
        return member

    def delete_member(self, id):
        member = self.get_member(id)
        if member is None:
            return None
        self.session.delete(member)
        self.session.commit()
        return member

    def get_raw_member(self, id):
        return self.session.query(self.entity).get(id)

    def get_collection(self, query):
        """ Search database objects based on query
        """
        self._query = query

        # Instanciate the query compiler 
        compiler = JsonQuery(self, **query)

        # Build query as SQL 
        if self.request.method == 'DELETE' \
                and self.entity.__table__.name.startswith('lb_doc_'):
            self.entity.__table__.__factory__ = [self.entity.__table__.c.id_doc]

        self.total_count = None
        factory = None
        if not self.request.params.get('result_count') in ('false', '0') \
                and getattr(self, 'result_count', True) is not False:
            self.total_count = 0
            count_over = func.count().over()
            factory = [count_over] + self.entity.__table__.__factory__

        # Impede a explosão infinita de cláusula over
        if factory is None:
            results = self.session.query(self.entity.__table__.__factory__)
        else:
            log.debug("Teste do query factory com explode de over: \n%s", factory)
            results = self.session.query(*factory)

        # Query results and close session
        self.session.close()

        # Filter results
        q = compiler.filter(results)

        if self.entity.__table__.name.startswith('lb_file_'):
            q = q.filter('id_doc is not null')

        if compiler.order_by is not None:
            for o in compiler.order_by:
                order = getattr(sqlalchemy, o)
                for i in compiler.order_by[o]: q = q.order_by(order(i))

        if compiler.distinct:
            q = q.distinct(compiler.distinct)

        if not 'limit' in query:
            compiler.limit = 10
        if not 'offset' in query:
            compiler.offset = 0

        self.default_limit = compiler.limit
        self.default_offset = compiler.offset

        # limit and offset results
        q = q.limit(compiler.limit)
        q = q.offset(compiler.offset)

        feedback = q.all()

        if len(feedback) > 0 and hasattr(self, 'count_over'):
            # The count must be the first column on each row
            self.total_count = int(feedback[0][0])

        # Return Results
        if query.get('select') == [ ] and self.request.method == 'GET':
            return [ ]

        return feedback

    def wrap_json_obj(self, obj):

        limit = 0 if self.default_limit is None else self.default_limit
        offset = 0 if self.default_offset is None else self.default_offset
        wrapped = dict(
            results = obj,
            limit = limit,
            offset = offset)
        if hasattr(self, 'total_count'):
            wrapped.update(result_count = self.total_count)
        return wrapped

    def get_member_id_as_string(self, member):
        id = self.get_member_id(member)
        if isinstance(id, string_types):
            return id
        else:
            return utils.object2json(id)

    def to_json(self, value, fields=None, wrap=True):
        obj = self.get_json_obj(value, fields, wrap)
        if getattr(self, 'single_member', None) is True and type(obj) is list:
            obj = obj[0]
        return utils.object2json(obj)

    def member2KeyedTuple(self, member):
        keys = list(member.__dict__.keys())
        values = list(member.__dict__.values())
        if '_sa_instance_state' in keys:
            i = keys.index('_sa_instance_state')
            del keys[i]
            del values[i]
        return KeyedTuple(values, labels=keys)
