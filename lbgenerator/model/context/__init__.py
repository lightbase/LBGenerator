
from pyramid.compat import string_types
import json
import inspect
import datetime
import sqlalchemy
from sqlalchemy import asc, desc
from pyramid_restler.model import SQLAlchemyORMContext
from lbgenerator.lib import utils
from lbgenerator import model
from lbgenerator.model import begin_session

class CustomContextFactory(SQLAlchemyORMContext):

    """ Default Factory Methods
    """

    def __init__(self, request):
        self.request = request
        self.base_name = self.request.matchdict.get('base')

    def session_factory(self):
        """ Connect to database and begin transaction
        """
        return begin_session()

    def get_base(self):
        """ Return Base object
        """
        return model.BASES.get_base(self.base_name)

    def set_base(self, base_json):
        """ Set Base object
        """
        return model.BASES.set_base(base_json)

    def get_cols(self):
        cols = tuple()
        for field in self.default_fields:
            if field != 'blob_doc':
                col = (getattr(self.entity, field),)
                cols += col
        if not 'id_doc' in self.default_fields and 'blob_doc' in self.default_fields:
            cols += (getattr(self.entity, 'id_doc'),)
        return cols

    def get_member(self, id):
        self.single_member = True
        q = self.session.query(self.entity)
        return q.get(id)

    def get_collection(self, select=None, distinct=False, order_by=None, limit=None,
                       offset=None, filters=None, literal=None):
        """ Search database objects
        """

        if select and select != '*':
            self.default_fields = list()
            for s in select: self.default_fields.append(s)

        cols = self.get_cols()
        q = self.session.query(*cols)
        self.session.close()

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

    def get_member_id_as_string(self, member):
        id = self.get_member_id(member)
        if isinstance(id, string_types):
            return id
        else:
            return json.dumps(id, cls=self.json_encoder)

    def to_json(self, value, fields=None, wrap=True):
        obj = self.get_json_obj(value, fields, wrap)
        if getattr(self, 'single_member', None) is True and type(obj) is list:
            obj = obj[0]
        return json.dumps(obj, cls=self.json_encoder, ensure_ascii=False)
