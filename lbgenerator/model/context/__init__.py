
from lbgenerator.model.entities import *
from lbgenerator.model import consistence
import json 
import inspect 
import requests 
import datetime
import sqlalchemy
from sqlalchemy import asc, desc
from sqlalchemy.orm.state import InstanceState
from pyramid_restler.model import SQLAlchemyORMContext
from lbgenerator.lib import utils
from lbgenerator.model.index import Index
from lbgenerator.model import begin_session
from lbgenerator.model import engine
from lbgenerator.model import metadata
from lbgenerator.model import get_bases
from lbgenerator.model import reg_hyper_class
from lbgenerator.model import doc_hyper_class

class CustomContextFactory(SQLAlchemyORMContext):

    def __init__(self, request):
        self.request = request
        self.base_name = self.request.matchdict.get('basename')
        if self.base_name:
            self.index = Index(self.base_name)

    def session_factory(self):
        return begin_session()

    def _execute(self, seq):
        """ Get next value from sequence.
        """
        seq.create(bind=engine)
        value = self.session.execute(seq)
        return value

    def get_cols(self):
        cols = tuple()
        for field in self.default_fields:
            if field != 'blob_doc':
                col = (getattr(self.entity, field),)
                cols += col
        if not 'id_doc' in self.default_fields and 'blob_doc' in self.default_fields:
            cols += (getattr(self.entity, 'id_doc'),)
        return cols

    def get_member(self, id, force=False):
        self.single_member = True
        if 'blob_doc' in self.default_fields and not force:
            q = self.session.query(*self.get_cols()).filter_by(id_doc=id)
            return q.all() or None
        q = self.session.query(self.entity)
        return q.get(id)

    def create_member(self, data):
        # CREATE MEMBER
        member = self.entity(**data)
        self.session.add(member)
        self.session.flush()

        # INDEX MEMBER
        if 'json_reg' in data:
            data = self.index.create(data)
        for name in data:
            setattr(member, name, data[name])
        self.session.commit()
        self.session.close()
        return member

    def update_member(self, id, data, index=True):
        member = self.get_member(id, force=True)
        if member is None:
            return None

        # UPDATE MEMBER
        if 'json_reg' in data and index is True:
            data = consistence.normalize(self.base_name, self.session, data)
        for name in data:
            setattr(member, name, data[name])
        self.session.flush()

        # INDEX MEMBER
        if 'json_reg' in data and index is True:
            data = self.index.update(id, data)
        for name in data:
            setattr(member, name, data[name])

        self.session.commit()
        self.session.close()
        return member

    def clear_del_data(self, id, member):
        for attr in member.__dict__:
            static_attrs = isinstance(member.__dict__[attr], InstanceState)\
            or attr == 'id_reg' or attr == 'dt_reg'
            if not static_attrs:
                setattr(member, attr, None)
        setattr(member, 'dt_reg_del', datetime.datetime.now())
        setattr(member, 'json_reg', '{"id_reg":%s}' % str(id))
        return member

    def delete_member(self, id, is_reg=False):
        member = self.get_member(id, force=True)
        if member is None:
            return None
        if is_reg:
            if self.index.delete(id):
                self.session.delete(member)
            else:
                member = self.clear_del_data(id, member)
        self.session.commit()
        self.session.close()
        return member

    def get_collection(self, select=None, distinct=False, order_by=None, limit=None,
                       offset=None, filters=None, literal=None):

        if select and select != '*':
            self.default_fields = list()
            for s in select: self.default_fields.append(s)

        cols = self.get_cols()
        q = self.session.query(*cols)

        def filter_query(q, f, expr='None'):
            field, operation, term = getattr(self.entity, f['field']), f['operation'], f['term']

            if operation == '=':
                q = q.filter(field == term)
            elif operation == 'contains':
                q = q.filter(field.contains(term))
            elif operation == 'like':
                q = q.filter(field.like(term))
            else: expr = 'self.entity.{0} {1} "{2}"'.format(f['field'], operation, term)
            return q.filter(eval(expr))

        if filters:
            if type(filters) is not list: raise Exception('filters must be list')
            for f in filters: q = filter_query(q, f)
        if literal:
            utils.is_sqlinject(str(literal))
            q = q.filter(literal)
        if type(select) is list and len(select) == 0:
            self.default_fields = list()
        if distinct:
            q = q.distinct()
        if order_by is not None:
            for o in order_by:
                order = getattr(sqlalchemy, o)
                for i in order_by[o]: q = q.order_by(order(i))

        self.total_count = q.count()

        frame = inspect.currentframe()
        k, a, w, v = inspect.getargvalues(frame)
        args = {i: v[i] for i in k if i != 'self'}

        kwargs = False
        for i in args:
            if args[i] is None or args[i] is False: pass
            else: kwargs = True

        if not kwargs:
            self.default_offset = 0
            self.default_limit = 10
        else:
            self.default_offset = None
            self.default_limit = None

        if offset is not None:
            self.default_offset = offset
        if limit is not None:
            self.default_limit = limit

        q = q.offset(self.default_offset)
        q = q.limit(self.default_limit)

        return q.all()

    def to_json(self, value, fields=None, wrap=True):
        obj = self.get_json_obj(value, fields, wrap)
        if fields is not None and len(fields) is 1 and fields[0] == 'json_reg' and wrap is False:
            obj = obj[0].get('json_reg')
        elif getattr(self, 'single_member', None) is True and type(obj) is list:
            obj = obj[0]

        return json.dumps(obj, cls=self.json_encoder, ensure_ascii=False)

    def wrap_json_obj(self, obj):
        count = len(obj)
        if hasattr(self, 'total_count'): count = self.total_count
        # Select no fields:
        if self.default_fields is not None and len(self.default_fields) is 0: obj = list()

        limit = getattr(self, 'default_limit', 10)
        limit = 0 if limit is None else limit
        offset = getattr(self, 'default_offset', 0)
        offset = 0 if offset is None else offset

        return dict(
            results = obj,
            result_count = count,
            limit = limit,
            offset = offset
        )
