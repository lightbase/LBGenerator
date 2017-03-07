
# TODO: Fix NULL casing, this will help:
#https://github.com/psycopg/psycopg2/blob/497247a52836e971b0b5a5779d0c5c60b98e654d/psycopg/adapter_list.c
#https://github.com/zzzeek/sqlalchemy/blob/master/lib/sqlalchemy/dialects/postgresql/base.py
#http://stackoverflow.com/questions/22485971/python-sqlalchemy-insert-array-postgres-with-null-values-not-possible
#https://groups.google.com/forum/#!msg/sqlalchemy/D5N9L4Ihgt8/0is1EGS0798J

# The explanation why I am using MetaData():
# For some reason the right metadata is raising a Mapper error, but not always,
# only when many requests are made. Weird.
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.types as dbtypes
from sqlalchemy.schema import Column, Table
from sqlalchemy.types import Integer, String, DateTime, Binary, Boolean
from sqlalchemy.schema import Sequence
from sqlalchemy.schema import MetaData
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSON

from .jsondbtype import BaseJSON, DocumentJSON, GUID

Base = declarative_base()


class LBBase(Base):
    """
    Bases Object-Relational Mapping. Base concept: Definition of data structure.
    Class used to mapp the 'lb_base' Table to object. 'lb_base' Table persists
    all Bases structures and it's metadata.
    """

    __tablename__ = 'lb_base'

    # @column id_base: The primary key for this table and uniquely identify each
    # base in the table.
    id_base = Column(Integer, primary_key=True)

    # @column name: The base name. Should accept only low-case characters
    # separated by underscore. Also should be a unique constraint, to ensure
    # all bases names will be unique.
    name = Column(String, nullable=False, unique=True)

    # @column struct: The base structure. The structure is a tree-format 
    # structure used to validate data to be inserted on database.
    struct = Column(String, nullable=False)

    # @column dt_base: The base creation date (date and time). 
    dt_base = Column(DateTime, nullable=False)

    # @column idx_exp: Index exportaction. Flag used to indicate if the base
    # needs to be indexed. Each document inserted on Base will be indexed if
    # this flag is true. The index engine is external to this API.
    idx_exp = Column(Boolean, nullable=False)

    # @column idx_exp_uri: Index exportaction URI (Uniform Resource Identifier).
    # Identifier used to index the documents. Accepted format is:
    # http://<IP>:<PORT>/<INDEX>/<TYPE>. If @column idx_exp is true, when
    # inserting a document to base, a HTTP request is sent to this URI.
    idx_exp_url = Column(String)

    # @column idx_exp_time: Index exportaction time. Time in seconds used by 
    # asynchronous indexer to sleep beetwen the indexing processes.
    idx_exp_time = Column(Integer)

    # @column file_ext: File extraction. Flag used by asynchronous text 
    # extractor. Indicates the need of extracting the text of the base files.
    file_ext = Column(Boolean, nullable=False)

    # @column file_ext_time: File extraction time. Time in seconds used by 
    # asynchronous extractor to sleep beetwen the extracting processes.
    file_ext_time = Column(Integer)

    # @column txt_mapping: Rotorna o mapeamento/configuração da 
    # indexaçao textual.
    txt_mapping = Column(String)

# Table factory are the default columns used when query object by API.
LBBase.__table__.__factory__ = [LBBase.__table__.c.id_base,
                                LBBase.__table__.c.struct]


class LBDocument():
    """
    Documents Object-Relational Mapping. Class used to mapp the 'lb_doc_<BASE>' 
    Table to object. Document concept:  document-oriented database 
    implementation differs on the details of this definition, in general, they 
    all assume documents encapsulate and encode data (or information) in some 
    standard formats or encodings. Encodings in use include XML, YAML, JSON 
    (this case), and BSON, as well as binary forms like PDF and Microsoft 
    Office documents (MS Word, Excel, and so on). For necessity, the binary 
    forms are stored in other table.
    """

    def __init__(self, id_doc, document, dt_doc=None, dt_last_up=None,
        dt_del=None, dt_idx=None, **kwargs):
        self.id_doc = id_doc
        self.document = document
        self.dt_doc = dt_doc
        self.dt_last_up = dt_last_up
        self.dt_del = dt_del
        self.dt_idx = dt_idx

        for k in kwargs:
            if isinstance(kwargs[k], list)\
                 and all(v is None for v in kwargs[k]):
                kwargs[k]= None # Set value to None if is an empty list
            elif kwargs[k] == '':
                kwargs[k]= None
        self.__dict__.update(kwargs)

def get_doc_table(__base__, __metadata__, **rel_fields):
    """
    @param base: The base name.
    @param metadata: A container object from sqlalchemy that keeps together 
    many different features of a database (or multiple databases) being 
    described.
    @param rel_fields: Dictionary at the format {field_name: field_obj} used
    to create adicional columns on the table.
    @return :Table object.

    Create a dynamic document Table object to be mapped with LBDocument.
    """

    COLUMNS = (
        #'lb_doc_%s' %(__base__), __metadata__,
        'lb_doc_%s' %(__base__), MetaData(),

        # @column id_doc: The primary key for this table and uniquely identify
        # each document in the table.
        Column('id_doc', Integer, Sequence('lb_doc_%s_id_doc_seq' %(__base__)),
            primary_key=True),

        # @column document: JSON encoded data wich represent a base record or 
        # registry. All insertions on this columns must obey the base structure.
        #Column('document', DocumentJSON, nullable=False),
        Column('document', JSON, nullable=False),

        # @column dt_doc: The document's creation date (date and time).
        Column('dt_doc', DateTime, nullable=False),

        # @column dt_last_up: The document's last updating date (date and time).
        Column('dt_last_up', DateTime, nullable=False),

        # @column dt_del: The document's date (date and time) of deletion. This 
        # date is filled when he normal deletion process failed when deleting
        # the document index. When it happens, the document is cleared up, 
        # leaving only it's metadata.
        Column('dt_del', DateTime),

        # @column dt_idx: The document's date (date and time) if indexing. All
        # routines that index the document must fill this field.
        Column('dt_idx', DateTime)
    )

    for rel_field in rel_fields:
        # Get liblightbase.lbbase.fields object.
        field = rel_fields[rel_field]
        custom_col = get_custom_column(field)
        COLUMNS += (custom_col,)

    # Create the Table object. extend_existing Indicates that this Table is 
    # already present in the given MetaData.
    table = Table(*COLUMNS, extend_existing=True)
    # Table factory are the default columns used when query object by API.
    table.__factory__ = [
        table.c.id_doc,
        table.c.document,
        table.c.dt_doc,
        table.c.dt_del]

    return table


def get_custom_column(field):
    # Get sqlalchemy.type object.
    col_type = getattr(dbtypes, field._datatype.__schema__.__dbtype__)

    # Transform columns type to array if necessary.
    if field.__dim__ > 0:
        col_type = ARRAY(col_type, dimensions=field.__dim__)

    # Add UNIQUE constraint if necessary.
    unique = True if 'Unico' in field.indices else False

    # Create Column object.
    custom_col = Column(field.name, col_type, unique=unique)
    return custom_col

class LBFile():
    """
    Files Object-Relational Mapping. Class used to mapp the 'lb_file_<BASE>' 
    Table to object. This entity stores computer files, and it's metadata.
    Files may contain any type of data, encoded in binary form for computer
    storage and processing purposes.
    """

    def __init__(self, id_file, id_doc, filename, file, mimetype, filesize,
            filetext=None, dt_ext_text=None):
        self.id_file = id_file
        self.id_doc = id_doc
        self.filename = filename
        self.file = file
        self.mimetype = mimetype
        self.filesize = filesize
        self.filetext = filetext
        self.dt_ext_text = dt_ext_text

def get_file_table(__base__, __metadata__):
    """
    @param base: The base name.
    @param metadata: A container object from sqlalchemy that keeps together 
    many different features of a database (or multiple databases) being 
    described.
    @return: Table object.

    Create a dynamic file Table object to be mapped with LBFile.
    """

    table = Table(
        #'lb_file_%s' %(__base__), __metadata__,
        'lb_file_%s' %(__base__), MetaData(),

        # @column id_file: The primary key for this table and uniquely identify
        # each file in the table.
        Column('id_file', GUID, primary_key=True),

        # @column id_doc: The primary key for document's table. Each file 
        # belongs to a document. 
        Column('id_doc', Integer),

        # @column name: Name used to identify a computer file stored in a file 
        # system. Different file systems impose different restrictions on 
        # filename lengths and the allowed characters within filenames. 
        Column('filename', String, nullable=False),

        # @column file: Sequence of bytes, which means the binary digits (bits) 
        # are grouped in eights. Bytes that are intended to be interpreted as 
        # something other than text characters.
        Column('file', Binary, nullable=False),

        # @column mimetype: Internet media type. Standard identifier used on the
        # Internet to indicate the type of data that a file contains. A media 
        # type is composed of a type, a subtype, and zero or more optional 
        # parameters. 
        Column('mimetype', String, nullable=False),

        # @column size: Measures the size of @column file in bytes. 
        Column('filesize', Integer, nullable=False),

        # @column text: Plain text (eletronix text) extracted from @ column
        # file.
        Column('filetext', String),

        # @column dt_ext_text: Date (date and time) of text extraction by
        # asynchronous text extractor.
        Column('dt_ext_text', DateTime),

        # Indicates that this Table is already present in the given MetaData.
        extend_existing=True,
    )

    # Table factory are the default columns used when query object by API.
    table.__factory__ = [table.c.id_file,
                        table.c.id_doc,
                        table.c.filename,
                        table.c.mimetype,
                        table.c.filesize,
                        table.c.filetext,
                        table.c.dt_ext_text
                        ]
    return table


class LB_Users(Base):

    __tablename__ = 'lb_users'

    id_user = Column(Integer, primary_key=True)
    nm_user = Column(String(10), nullable=False, unique=True)
    email_user = Column(String, unique=True)
    passwd_user = Column(String, nullable=False)
    js_auth = Column(String, nullable=False)
    dt_cad = Column(DateTime, nullable=False)
    in_active = Column(Boolean, nullable=False)


class LBIndexError(Base):
    """
    Documents Error Object-Relational Mapping. 
    """
    __tablename__ = 'lb_index_error'

    # @column id_error: The primary key for this table and uniquely identify
    # each error.
    id_error = Column(Integer, Sequence('lb_index_error_seq'), primary_key=True)

    # @column name: The base name. Should accept values from lb_base.name 
    base = Column(String, nullable=False)

    # @column id_doc: The document identifier.
    id_doc = Column(Integer, nullable=False)

    # @column dt_error: The document creation date.
    dt_error = Column(DateTime, nullable=False)

    # @column msg_error: The produced error message.
    msg_error = Column(String)

# Table factory are the default columns used when query object by API.
LBIndexError.__table__.__factory__ = list(LBIndexError.__table__.c)


class Lb_Txt_Idx(Base):
    """
    Modelo de dados (ORM) da table "lb_txt_idx". Nesta table são
    guardadas as configurações de índices textuais.
    """
    __tablename__ = 'lb_txt_idx'

    # @column id_idx: The primary key for this table.
    id_idx = Column(Integer, Sequence('lb_txt_idx_id_idx_seq'), primary_key=True)

    # @column nm_idx: Nome único p/ o índice criado.
    nm_idx = Column(String, nullable=False)

    # @column struct: Estrutura da base.
    struct = Column(String, nullable=False)

    # @column cfg_idx: Configuração de índice a ser submetida no ES.
    cfg_idx = Column(String, nullable=False)

    # @column dt_crt_idx: Data de criação do registro.
    dt_crt_idx = Column(DateTime, nullable=False)

    # @column dt_upt_idx: Data do último update do registro.
    dt_upt_idx = Column(DateTime, nullable=False)

    # @column url_idx: URL de indexação.
    url_idx = Column(String, nullable=False)

    # @column actv_idx: Se o registro está ativo ou não.
    actv_idx = Column(Boolean, nullable=False)

# Table factory are the default columns used when query object by API.
Lb_Txt_Idx.__table__.__factory__ = [Lb_Txt_Idx.__table__.c.id_idx,
                                Lb_Txt_Idx.__table__.c.cfg_idx]
