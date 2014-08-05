
from . import CustomContextFactory
from ..index import Index
from .. import document_entity
from .. import file_entity
from ...lib import utils
from liblightbase.lbdocument import Tree
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.util import KeyedTuple
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import and_
import datetime

class DocumentContextFactory(CustomContextFactory):

    """ Document Factory Methods.
    """

    def __init__(self, request):
        super(DocumentContextFactory, self).__init__(request)

        # liblightbase.lbbase.Base object
        base = self.get_base()

        # LBDoc_<base> object (mapped ORM entity).
        self.entity = document_entity(self.base_name, **base.relational_fields)

        # LBFile_<base> object (mapped ORM entity).
        self.file_entity = file_entity(self.base_name)

        # Index object 
        self.index = Index(base, self.get_full_document)

    def create_files(self, member, files):
        """
        Create files (actually update id_doc, because file already exists)
        in database.
        @param files: List of file id's to create in database.
        """
        if len(files) > 0:
            stmt = update(self.file_entity.__table__).where(
                self.file_entity.__table__.c.id_file.in_(files))\
                .values(id_doc=member.id_doc)
            self.session.execute(stmt)

    def delete_files(self, member, files):
        """
        Will delete files that are not present in document.
        @param member: LBDoc_<base> object (mapped ORM entity).
        @param files: List of files ids present in document.
        """
        stmt = delete(self.file_entity.__table__).where(
        and_(self.file_entity.__table__.c.id_doc==member.id_doc,
             self.file_entity.__table__.c.id_file.notin_(files)))
        self.session.execute(stmt)

    def create_member(self, data):
        """ 
        @param data: dictionary at the format {column_name: value}.
        Receives the data to INSERT at database (table lb_doc_<base>).
        Here the document will be indexed, and files within it will be created.
        """
        member = self.entity(**data)
        self.session.add(member)
        data = self.index.create(data)
        self.create_files(member, data['__files__'])
        for name in data:
            setattr(member, name, data[name])
        self.session.commit()
        self.session.close()
        return member

    def update_member(self, member, data, index=True):
        """ 
        Receives the data to UPDATE at database (table lb_doc_<base>). 
        Here the document will be indexed, files within it will be created,
        and files that are not in document will be deleted.
        @param member: LBDoc_<base> object (mapped ORM entity).
        @param data: dictionary at the format {column_name: value}.
        @param index: Flag that indicates the need of indexing the
        document. 
        """
        if index:
            data = self.index.update(member.id_doc, data)
        self.delete_files(member, data['__files__'])
        self.create_files(member, data['__files__'])
        for name in data:
            setattr(member, name, data[name])
        self.session.commit()
        self.session.close()
        return member

    def delete_member(self, id):
        """ 
        @param id: primary key (int) of document.

        Query the document object, verify the flag `dt_del`. If setted,
        that means that this document was deleted once, but it's index was not
        successfull deleted. So we delete the document. If not, will try to
        delete it's index and document. In case of failure, will SET all 
        columns to NULL and clear document, leaving only it's metadata.
        """
        member = self.get_member(id) # Query member.
        if member is None:
            return None

        if member.dt_del is not None:
            self.session.delete(member) # DELETE document.

        elif self.index.delete(id): # Try to remove index.
            self.session.delete(member) # DELETE document.

        else:
            member = self.clear_del_data(member) # Clear document.

        self.delete_files_by_document(id) # DELETE referenced files.

        self.session.commit() # COMMIT transaction.
        self.session.close() # Close session.

        return member

    def clear_del_data(self, member):
        """ 
        @param member: LBDoc_<base> object (mapped ORM entity).

        This method should be called when index deletion was not possible.
        Will SET NULL to all columns leaving only document's metatada, and
        `dt_del`. 
        """
        document = utils.json2object(member.document)
        dt_del = datetime.datetime.now()
        document['_metadata']['dt_del'] = dt_del
        cleared_document = {'_metadata':document['_metadata']}

        for attr in member.__dict__:
            static_attrs = isinstance(member.__dict__[attr], InstanceState)\
            or attr in document['_metadata'].keys()
            if not static_attrs:
                setattr(member, attr, None)
        setattr(member, 'dt_del', dt_del)
        setattr(member, 'document', cleared_document)
        return member

    def delete_files_by_document(self, id):
        """ All docs are relationated with a document.
            This method deletes all docs referenced by param: id
        """
        self.session.query(self.file_entity)\
            .filter_by(id_doc = id).delete()

    def get_full_document(self, document, close_session=True):
        """ This method will return the document with files texts
            within it.
        """
        id = document['_metadata']['id_doc']
        file_cols = (
           self.file_entity.id_file,
           self.file_entity.filetext,
           self.file_entity.dt_ext_text
        )
        dbfiles = self.session.query(*file_cols).filter_by(id_doc= id).all()
        if close_session:
            self.session.close()
        files = { }
        if dbfiles:
            for dbfile in dbfiles:
                files[dbfile.id_file] = dict(
                    filetext=dbfile.filetext,
                )
        return self.put_doc_text(document, files)

    def put_doc_text(self, document, files):
        """ This method will parse a document, find files within it,
            and then update each file (with text, if exists)
        """
        if type(document) is dict:
            _document = document.copy()
        elif type(document) is list:
            _document = {document.index(i): i for i in document}
        for k, v in _document.items():
            if type(v) is dict and utils.is_file_mask(v):
                _file = files.get(v['id_file'])
                if _file: v.update(_file)
            elif type(v) is dict or type(v) is list:
                document[k] = self.put_doc_text(v, files)
        return document

    def member_to_dict(self, member, fields=None):
        """
        @param member: LBDoc_<base> object (mapped ORM entity).

        Converts @member object to SQLAlchemy's KeyedTuple, and then to
        Python's dictionary. Will also prune the dictionary member, if
        user send some nodes on query.
        """
        if not isinstance(member, KeyedTuple):
            member = self.member2KeyedTuple(member)

        # Get document as dictionary object.
        factory = self.entity.__table__.__factory__[1].name
        dict_member = member._asdict()[factory]

        fields = getattr(self,'_query', {}).get('select')
        if fields and not '*' in fields:
            # Will prune tree nodes.
            # dict_member can be None if method could not find any fileds
            # matching the nodes list.
            dict_member = Tree(dict_member).prune(nodes=fields)

        return dict_member

    def to_json(self, value, fields=None, wrap=True):
        obj = self.get_json_obj(value, fields, wrap)
        if getattr(self, 'single_member', None) is True and type(obj) is list:
            obj = obj[0]
        return utils.object2json(obj)

    def get_files_text_by_document_id(self, id_doc, close_session=True):
        """
        @param id_doc: id from document 
        @param close_session: If true, will close current session, 
        else will not.

        This method will return a dictonary in the format {id_file: filetext},
        with all docs referenced by @param: id_doc
        """
        # Query documents
        files = self.session.query(self.file_entity.id_file,
            self.file_entity.filetext).filter_by(id_doc=id_doc).all() or [ ]

        if close_session is True:
            # Close session if param close_session is True
            self.session.close()

        files = { }
        for file_ in files:
            # Build dictionary
            files[file_.id_file] = file_.filetext

        return files

