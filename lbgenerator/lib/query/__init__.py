# -*- coding: utf-8 -*-
from .select import SelectQuery
from .filter import FilterQuery


class JsonQuery():

    # NOTE: Trata um query no formato "json"! By Questor
    def __init__(self, context, select = None, from_ = None, where = None, 
            having = None, literal = None, limit = None, offset = None, 
            alias = None, order_by = None, distinct = None, full_reg = False):

        self.context = context

        cache = getattr(context, 'cache', None)

        if not cache:
            context.cache = QueryCache(context)

        self.from_ = from_
        self.select = SelectQuery(context, select, alias=alias)

        if literal:
            self.where = FilterQuery(context, literal)
        else:
            self.where = FilterQuery(context, where)

        self.having = having
        self.limit = limit
        self.offset = offset
        self.order_by = order_by
        self.distinct = distinct
        self.full_reg = full_reg

    def build_query(self):
        """ Build the SELECT list as SQL
        """
        return self.select.column_list()

    def filter(self, results):
        """ Apply a filter over the query
        """
        results = self.where.filter(results)

        for column in self.context.cache.__order_by__:
            results = results.order_by(column)

        return results

    @property
    def from_(self):
        return self._from

    @from_.setter
    def from_(self, f):
        """ Build Sub Selects in FROM clause as SQL
        """
        if f is None:
            self._from = self.context.entity

        elif isinstance(f, str):
            # Maybe we will need other tables
            self._from = self.context.entity

        elif isinstance(f, dict):
            subq = self.context.cache.build_subqueries(f)
            self._from = subq.c

        else:
            raise Exception('Malformed FROM clause. Expected object of type dict or string, but found %s' % f)

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, l):
        if l is None:
            self._limit = l
        elif isinstance(l, int):
            self._limit = l
        else:
            try:
                self._limit = int(l)
            except ValueError:
                raise Exception('Malformed LIMIT clause. Expected object of type int, but found %s' % l)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, o):
        if o is None:
            self._offset = o
        elif isinstance(o, int):
            self._offset = o
        else:
            try:
                self._offset = int(o)
            except ValueError:
                raise Exception('Malformed OFFSET clause. Expected object of type int, but found %s' % o)

class QueryCache():

    def __init__(self, context):
        self.context = context

        # Columns retriever
        self.__columns__ = { }

        # Columns to order by
        self.__order_by__ = [ ]

    def build_subqueries(self, from_clause):

        query = JsonQuery(self.context, **from_clause).build_query()
        alias = from_clause.get('alias', None)
        subquery = self.context.session.query(*query).subquery(alias)

        for column in subquery.c:
            col_name =  subquery.corresponding_column(column).name
            self.__columns__[col_name] = column

        return subquery

    def find_col(self, name):
        """ Try to find column
        """
        try:
            return self.__columns__[name]
        except KeyError:
            raise KeyError('Column "%s" not Found' % name)

    def add_col(self, name, alias, col):
        self.__columns__[name] = col
        self.__columns__[alias] = col

    def add_order(self, col):
        self.__order_by__.append(col)