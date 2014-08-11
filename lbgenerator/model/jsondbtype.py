from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.types import VARCHAR
from sqlalchemy.types import CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import Column
from ..lib import utils
import uuid

class BaseJSON(TypeDecorator):
    """
    Represents an immutable structure as a json-encoded string.
    """

    impl = JSON

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

    impl = JSON

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = utils.object2json(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = utils.json2object(value)
        return value

class GUID(TypeDecorator):

    """
    Platform-independent GUID type.
    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """

    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            uuid.UUID(value)
            return value


