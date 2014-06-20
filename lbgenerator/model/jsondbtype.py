from sqlalchemy.types import TypeDecorator, VARCHAR
from ..lib import utils

class BaseJSON(TypeDecorator):
    """
    Represents an immutable structure as a json-encoded string.
    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = utils.object2json(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = utils.json2object(value)
        return value

class DocumentJSON(TypeDecorator):
    """
    Represents an immutable structure as a json-encoded string.
    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = utils.object2json(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = utils.json2object(value)
        return value


