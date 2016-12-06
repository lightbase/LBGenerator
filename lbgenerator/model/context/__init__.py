import json

import sqlalchemy
import logging
from sqlalchemy.sql.expression import func
from sqlalchemy.util import KeyedTuple
from sqlalchemy import asc, desc
from pyramid.security import Deny
from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.compat import string_types
from pyramid.security import Authenticated
from pyramid.security import ALL_PERMISSIONS
from pyramid_restler.model import SQLAlchemyORMContext
from beaker.cache import cache_region
from beaker.cache import region_invalidate
from ...lib import cache

from ... import model
from ...lib import utils
from ...lib.query import JsonQuery
from ...model import begin_session
from ...lib.cache_master import CacheMaster

log = logging.getLogger()


class CustomContextFactory(SQLAlchemyORMContext, CacheMaster):
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

    def __init__(self, request, target_field=None):
        self.request = request
        self.base_name = self.request.matchdict.get('base')

        # NOTE: P/ uso da classe "CacheMaster" que é herdada pela 
        # classe atual! By Questor
        self.target_field = target_field

    def session_factory(self):
        """ Connect to database and begin transaction
        """
        if getattr(self, 'overwrite_session', False) is True:
            return self.__session__
        return begin_session()

    def get_base(self):
        """ Return Base object
        """

        '''
        NOTE: O seguinte tipo é o que consta em "model.BASES"!
        <lbgenerator.lib.generator.BaseMemory object>

        Retorna a estrutura da base (json) convertida para dict.
        Essa base pode vir do banco de dados ou da memória. Essas
        estruras são guardadas em memória "on demand", ou seja,
        na primeira vez que determinada estrutura de base é
        requerida esse processo acontece! By Questor
        '''
        return model.BASES.get_base(self.base_name)

    def set_base(self, base_json):
        """ Set Base object
        """
        return model.BASES.set_base(base_json)

    def get_member(self, id, close_sess=True):
        self.single_member = True
        q = self.session.query(self.entity)
        member = q.get(id)
        # Now closes session in the view instead of here - DCarv
        # if close_sess:
        #     self.session.close()
        return member

    def delete_member(self, id):
        member = self.get_member(id)
        if member is None:
            return None
        self.session.delete(member)
        # Now commits and closes session in the view instead of here
        # flush() pushes operations to DB's buffer - DCarv
        self.session.flush()

        # NOTE: Clear all caches on this case! By Questor
        cache.clear_cache()

        return member

    def get_raw_member(self, id):
        return self.session.query(self.entity).get(id)

    def get_collection(self, query):
        """Search database objects based on query.

        @param query: Query de busca.
        """

        # NOTE: Seta a query na instância da classe.
        self._query = query

        # NOTE: Instanciate the query compiler.
        compiler = JsonQuery(self, **query)

        # NOTE: Build query as SQL.
        if self.request.method == 'DELETE' \
                and self.entity.__table__.name.startswith('lb_doc_'):

            '''
            NOTE: Seta que a lista de ocorrência terá apenas o campo 
            "id_doc" p/ os registros! By Questor
            '''
            self.entity.__table__.__factory__ = [self.entity.__table__.c.id_doc]

        '''
        NOTE: "__factory__" em "self.entity.__table__.__factory__", 
        pode ser, a princípio, entendido como um "place holder" que vai 
        acomodar cada registro conforme o modelo definido neste. Esse 
        modelo vem originalmente do método "get_doc_table(__base__, 
        __metadata__, **rel_fields)" do arquivo "lbgenerator/model/
        entities.py", mas pode ser modificado conforme logo acima... 
        By Questor
        '''
        self.total_count = None
        factory = None
        count_over = None

        if not self.request.params.get('result_count') in ('false', '0') \
                and getattr(self, 'result_count', True) is not False:
            self.total_count = 0
            count_over = func.count().over()
            factory = [count_over] + self.entity.__table__.__factory__

        # NOTE: Impede a explosão infinita de cláusula over.
        if factory is None:
            q = self.session.query(*self.entity.__table__.__factory__)
        else:
            q = self.session.query(*factory)

        '''
        NOTE: Query "q" e feche a sessão. Aqui é disparada a busca 
        conforme o factory acima! By Questor
        '''
        # Now commits and closes session in the view instead of here
        # flush() pushes operations to DB's buffer - DCarv
        self.session.flush()

        '''
        NOTE: "Compiler.filter()" faz a chamada "self.where.filter()" que 
        assim como "self.session.query()" fazem parte! By Questor
        '''
        q = compiler.filter(q)

        # NOTE: Ordena busca se for o caso.
        if compiler.order_by is not None:
            for o in compiler.order_by:
                order = getattr(sqlalchemy, o)
                for i in compiler.order_by[o]: q = q.order_by(order(i))

        '''
        NOTE: In a table, a column may contain many duplicate values; 
        and sometimes you only want to list the different (distinct) 
        values. The DISTINCT keyword can be used to return only 
        distinct (different) values! By Questor
        '''
        if compiler.distinct:
            q = q.distinct(compiler.distinct)

        # NOTE: Obtêm limit e offset e seta no "compiler"! By Questor
        if not 'limit' in query:
            compiler.limit = 10
        if not 'offset' in query:
            compiler.offset = 0

        # TODO: Pq limit e offset default? Tá meio ezquisito isso 
        # aqui... By Questor
        self.default_limit = compiler.limit
        self.default_offset = compiler.offset

        # NOTE: Seta limit e offset em "q"! By Questor
        q = q.limit(compiler.limit)
        q = q.offset(compiler.offset)


        # NOTE: "q" é um objeto q contêm a query de busca setada e 
        # herda funcionalidades do SQLAlchemy.

        # NOTE: "feedback" contêm os registros localizados. O método 
        # ".all()" dispara a busca por fim! By Questor
        feedback = q.all()

        if len(feedback) > 0 and count_over is not None:

            # NOTE: The count must be the first column on each 
            # row! By Questor
            self.total_count = int(feedback[0][0])

        # NOTE: Caso não seja localizado nenhum registro.
        if query.get('select') == [] and self.request.method == 'GET':
            return []

        if compiler.full_reg:
            # NOTE: Como "feedback" é um tipo referência nos apropriamos 
            # naturalmente dessa qualidade para poupar memória! By Questor
            self.full_documents(feedback)

        return feedback

    def full_documents(self, members):
        """À partir de uma lista de ocorrências dada insere os textos 
        extraídos dos arquivos, se houverem, na mesma!

        @param members: Saída de uma consulta usando o SQLAlchemy.
        """

        # NOTE: Obtêm a lista de id's dos "docs" para pesquisar nos 
        # "files" ! By Questor
        list_id_doc = []
        for member in members:
            list_id_doc.append(member.id_doc)

        self.get_full_documents(list_id_doc, members)

    def wrap_json_obj(self, obj):
        """
        Wrap the object as JSON

        :param obj: Object dict
        :return: wrapped object
        """
        limit = 0 if self.default_limit is None else self.default_limit
        offset = 0 if self.default_offset is None else self.default_offset
        wrapped = dict(
            results=obj,
            limit=limit,
            offset=offset)
        if hasattr(self, 'total_count'):
            wrapped.update(result_count=self.total_count)
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

    def get_collection_cached(self,
                              query,
                              cache_key,
                              cache_type='default_term',
                              invalidate=False):
        """
        Get cached results collection

        :param query: Search query
        :param cache_key: Key concerning cache expire time
            short_term: 60 seconds
            default_term: 300 seconds
            long_term: 3600 seconds
        :param invalidate: invalidate cache or not
        :return: Collection JSON
        """
        if invalidate:
            region_invalidate(_get_collection_cached, None, query)

        @cache_region(cache_type, cache_key)
        def _get_collection_cached(query):
            """
            Return cached collection

            :param query: Query to be executed against function mode
            :return: result
            """
            response = {
                'results': self.get_collection(query),
                'limit': self.default_limit,
                'offset': self.default_offset,
                'total_count': self.total_count
            }
            return response

        response = _get_collection_cached(query)

        # Fix parameters
        self.default_limit = response['limit']
        self.default_offset = response['offset']
        self.total_count = response['total_count']

        # Return results
        return response['results']

    def get_member_cached(self,
                          id,
                          cache_key,
                          close_sess=True,
                          cache_type='default_term',
                          invalidate=False):
        """
        Get member cached function

        :param id: Object instance ID for cache
        :param close_sess: Session close after execution
        :param cache_key: Key concerning cache expire time
            short_term: 60 seconds
            default_term: 300 seconds
            long_term: 3600 seconds
        :param invalidate: Invalidate this cache
        """
        if invalidate:
            region_invalidate(_get_member_cached, None, id, close_sess)

        @cache_region(cache_type, cache_key)
        def _get_member_cached(id, close_sess):
            """
            Execute when there's no cache
            """
            log.debug("Creating cache for region %s and key %s", cache_type, cache_key)
            return self.get_member(id, close_sess)

        self.single_member = True

        return _get_member_cached(id, close_sess)
