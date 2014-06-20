
from .column import ColumnQuery

class SelectQuery():

    wildcard = '*'

    def __init__(self, context, select, alias=None):
        self.context = context
        self.select = select
        self.alias = alias

    def default_list(self):
        columns = self.context.entity.__table__.c
        return [column for column in columns if column.name != 'blob_doc']

    def column_list(self):

        if self.select == self.wildcard or self.select is None:
            return self.default_list()

        _column_list = [ ]

        for obj in self.select:

            if isinstance(obj, str):
                item = ColumnQuery(self.context, obj).all_expr()

            elif isinstance(obj, dict):
                item = ColumnQuery(self.context, **obj).all_expr()

            else:
                raise Exception('Malformed SELECT clause. Expected type str or dict for COLUMN, \
                    but found %s' % obj)

            _column_list.append(item)

        return _column_list

    @property
    def select(self):
        return self._select

    @select.setter
    def select(self, s):

        if s == self.wildcard or s is None:
            self._select = s

        elif isinstance(s, list):
            self._select = s

        else:
            raise Exception('Malformed SELECT clause. Expected type list but found %s' % s)

    @property
    def alias(self):
        return self._alias

    @alias.setter
    def alias(self, a):

        if a is None or isinstance(a, str):
            self._alias = a

        else:
            raise Exception('Malformed SELECT clause. Expected type str for ALIAS but found %s' % a)

