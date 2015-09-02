
from sqlalchemy import asc, desc
from sqlalchemy.sql import func

class ColumnQuery():

    __order_by__ = [ ]

    def __init__(self, context, column, alias=None, aggregate=None, distinct=False,
            transform=None, result_field=None, params=[ ], order_by=None):

        self.context = context

        # @param column: the column name (required).
        self._column = getattr(context.entity, column)

        # @param alias: used to define a column alias, which otherwise defaults to the column name.
        self._alias = alias or self._column.name

        try:
            # If column alredy exists, get it, else add it so we can finf later
            self._column = self.context.cache.find_col(self._column.name)
        except KeyError:
            self.context.cache.add_col(self._column.name, self._alias, self._column)

        # @param distinct: takes a value of true or false. 
        # It concerns the use of DISTINCT clauses.
        self._distinct = distinct

        # @param aggregate: takes a value of true or false. 
        # It concerns the use of GROUP BY clauses.
        self._aggregate = aggregate

        # @param result_field: used with "transform"; 
        # specifies an output column of a function that returns multiple columns at a time.
        self._result_field = result_field

        # @param params: used with "transform"; 
        # provides a list of parameters for the function. They may be strings, numbers, or nulls
        self._params = params

        # @param transform: the name of an SQL function to be called.
        self._transform = transform

        # @param order_by: takes a value of "asc" or "desc". 
        # It concerns the use of ORDER_BY clauses.
        self._order_by = order_by

    def all_expr(self):
        self.transform().alias().distinct().order_by()
        return self._column

    def alias(self):
        self._column = self._column.label(self._alias)
        return self

    def transform(self):
        if self._transform:
            self._column = getattr(func, self._transform)(*self._params)
        return self

    def distinct(self):
        if self._distinct:
            self._column = self._column.distinct()
        return self

    def aggregate(self):
        return self

    def result_field(self):
        return self

    def order_by(self):

        if self._order_by:
            order = self._order_by(self._column)
            self.context.cache.add_order(order)

        return self

    @property
    def _order_by(self):
       return self._order_by_

    @_order_by.setter
    def _order_by(self, ob):

        if ob is None:
            self._order_by_ = ob

        elif ob == 'desc':
            self._order_by_ = desc

        elif ob == 'asc':
            self._order_by_ = asc

        else:
            raise Exception('ORDER_BY clause must be "asc" or "desc"')

    @property
    def _distinct(self):
       return self._distinct_

    @_distinct.setter
    def _distinct(self, d):

        if d is None:
            self._distinct_ = d

        elif isinstance(d, bool):
            self._distinct_ = d

        else:
            raise Exception('DISTINCT clause must be of type bolean, but found %s' % d)

    @property
    def _transform(self):
       return self._transform_

    @_transform.setter
    def _transform(self, t):

        if t is None:
            self._transform_ = t

        elif isinstance(t, str):
            self._transform_ = t

        else:
            raise Exception('Transform function must be of type string, but found %s' % t)

    @property
    def _params(self):
       return self._params_

    @_params.setter
    def _params(self, p):

        if isinstance(p, list):
            self._params_ = [self.context.cache.find_col(param[1:]) if str(param).startswith('+') \
                else param for param in p]

        else:
            raise Exception('Params must be of type list, but found %s' % p)




