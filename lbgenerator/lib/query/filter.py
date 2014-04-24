class FilterQuery():

    parser = None

    def __init__(self, context, where):
        self.context = context
        self.where = where

    def filter(self, results):
        """ Build WHERE clause as SQL
        """
        return self.parser(self.where, results)

    @property
    def where(self):
        return self._where

    @where.setter
    def where(self, w):

        if not w:
            self.parser = self.parse_none

        elif isinstance(w, dict):
            self.parser = self.parse_dict

        elif isinstance(w, list):
            self.parser = self.parse_list

        elif isinstance(w, str):
            self.parser = self.parse_str

        else:
            raise Exception('Malformed WHERE clause. Expected type dict, list or string, but %s found' % w)

        self._where = w

    def parse_none(self, where_clause, results):
        """ Filter results if no where_clause 
        """
        return results

    def parse_dict(self, where_clause, results):
        """ Filter results when where_clause is a dict 
        """
        for field, clause in where_clause.items():

            if str(field).startswith('+'):
                column = self.context.cache.find_col(field[1:])
            else:
                column = getattr(self.context.entity, field)

            if isinstance(clause, dict):
                op, value = clause.popitem()

                if str(value).startswith('+'):
                    value = self.context.cache.find_col(value[1:])

                results = results.filter(Compare(column, op).to(value))

            elif isinstance(clause, str):
                results = results.filter(Compare(column, '=').to(clause))

        return results

    def parse_list(self, where_clause, results):
        """ Filter results when where_clause is a list
        """
        for item in where_clause:

            if isinstance(item, dict):
                results = self.parse_dict(item, results)

            elif isinstance(item, list):
                pass

        return results

    def parse_str(self, where_clause, results):
        """ Filter results when where_clause is a string 
        """
        return results.filter(where_clause)

class Compare():

    def __init__(self, column, operation):
        self.column = column
        self.operation = operation

    @property
    def __mapping__(self):
        return {
            '=': self.equals,
            '<>': self.differs,
            '!=': self.differs,
            '<': self.less,
            '>': self.greater,
            '<=': self.lessequals,
            '>=': self.greaterequals,
            #'~': self.,
            #'~*': self.,
            #'!~': self.,
            #'!~*': self.,
            'like': self.like,
            'ilike': self.ilike,
            'similar': self.similar
        }

    def to(self, value):
        method = self.__mapping__[self.operation]
        if method is None:
            raise NotImplementedError('Operator "%s" not implemented' % op)
        else:
            return method(value)

    def equals(self, value):
       return self.column == value

    def differs(self, value):
        return self.column != value

    def less(self, value):
        return self.column < value

    def greater(self, value):
        return self.column > value

    def lessequals(self, value):
        return self.column <= value

    def greaterequals(self, value):
        return self.column >= value

    def like(self, value):
        return self.column.like(value)

    def ilike(self, value):
        return self.column.ilike(value)

    def similar(self, value):
        return self.column.similar(value)
