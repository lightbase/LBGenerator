
from pyramid.compat import string_types
import json
import sqlalchemy
from sqlalchemy.util import KeyedTuple
from sqlalchemy import asc, desc
from pyramid_restler.model import SQLAlchemyORMContext
from lbgenerator.lib import utils
from lbgenerator import model
from lbgenerator.model import begin_session
from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import Deny
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Authenticated
from lbgenerator.lib.query import JsonQuery

class CustomContextFactory(SQLAlchemyORMContext):

    """ Default Factory Methods
    """

    json_encoder = utils.DefaultJSONEncoder

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
        return begin_session()

    def get_base(self):
        """ Return Base object
        """
        return model.BASES.get_base(self.base_name)

    def set_base(self, base_json):
        """ Set Base object
        """
        return model.BASES.set_base(base_json)

    def get_member(self, id):
        self.single_member = True
        q = self.session.query(self.entity)
        return q.get(id)

    def get_collection(self, query):
        """ Search database objects based on query
        """
        """ 
        kw = {
            'select':[
                #'id_reg',
                {'column': 'json_reg', 'distinct': False, 'order_by':'asc'}
                #{'column': 'json_reg','transform': 'upper', 'params':['+json_reg'], 'distinct': True}
            ],
            'from_': {
                'select':[
                    {'column': 'json_reg'},
                    {'column': 'a1', 'alias':'len1', 'transform':'array_length', 'params':['+a1', 1]},
                    {'column': 'a1', 'alias':'idx1', 'transform':'generate_subscripts', 'params':['+a1', 1]},
                    {'column': 'a1', 'alias':'val1', 'transform':'unnest', 'params':['+a1']},
                    {'column': 'a2', 'alias':'len2', 'transform':'array_length', 'params':['+a2', 1]},
                    {'column': 'a2', 'alias':'idx2', 'transform':'generate_subscripts', 'params':['+a2', 1]},
                    {'column': 'a2', 'alias':'val2', 'transform':'unnest', 'params':['+a2']},
                ]
            },
            'where': [
               {'+val1': {'=': '20'}},
               {'+idx1': {'=': '+idx2'}},
               {'+val2': {'=': '3'}},
               {'+idx1': {'=': '1'}}
            ],
            'literal': "val1='20' AND idx1=idx2 AND val2='3' AND idx1='1'"
        }
        """

        self._query = query

        # Instanciate the query compiler 
        compiler = JsonQuery(self, **query)

        # Build query as SQL 
        sql = compiler.build_query()

        self.default_fields = [col.name for col in sql]

        # Query results and close session
        results = self.session.query(*sql)
        self.session.close()

        # Filter results
        q = compiler.filter(results)

        # TODO: GET RID OF IT
        if compiler.order_by is not None:
            for o in compiler.order_by:
                order = getattr(sqlalchemy, o)
                for i in compiler.order_by[o]: q = q.order_by(order(i))

        if compiler.distinct:
            q = q.distinct()

        # Set total count for pagination 
        self.total_count = q.count()

        # TODO: GET RID OF IT -- from here
        has_any_query = False
        for k, v in query.items():
            if v is None or v is False: pass
            else: has_any_query = True

        if has_any_query:
            self.default_offset = None
            self.default_limit = None
        else:
            self.default_offset = 0
            self.default_limit = 10

        if compiler.offset is not None:
            self.default_offset = compiler.offset
        if compiler.limit is not None:
            self.default_limit = compiler.limit

        q = q.offset(self.default_offset)
        q = q.limit(self.default_limit)

        # -- until here

        """
        if not 'limit' in query:
            compiler.limit = 10
        if not 'offset' in query:
            compiler.offset = 0

        self.default_limit = compiler.limit
        self.default_offset = compiler.offset

        # limit and offset results
        q = q.limit(compiler.limit)
        q = q.offset(compiler.offset)
        """

        # Return Results
        return q.all()

    def wrap_json_obj(self, obj):

        limit = 0 if self.default_limit is None else self.default_limit
        offset = 0 if self.default_offset is None else self.default_offset

        return dict(
            results = obj,
            result_count = self.total_count,
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

    def member2KeyedTuple(self, member):
        keys = list(member.__dict__.keys())
        values = list(member.__dict__.values())
        keys.pop(0) # _sa_instance_state object
        values.pop(0) # _sa_instance_state object
        return KeyedTuple(values, labels=keys)
