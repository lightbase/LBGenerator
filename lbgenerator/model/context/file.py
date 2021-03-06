import logging
from threading import Thread
from collections import Iterable

from sqlalchemy import and_
from sqlalchemy import insert
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy.util import KeyedTuple
from sqlalchemy.orm.state import InstanceState
from liblightbase.lbdoc.doctree import DocumentTree

from ...lib import cache
from .. import file_entity
from . import CustomContextFactory


class FileContextFactory(CustomContextFactory):
    """ Document Factory Methods
    """

    def __init__(self, request):
        super(FileContextFactory, self).__init__(request)
        self.entity = file_entity(self.base_name)

    def get_member(self, id):
        self.single_member = True

        # NOTE I: We don't want to query hole file when searching! By John Doe

        # NOTE II: So the bytes column will not be in query list this time! By John Doe
        cols = self.entity.__table__.__factory__

        q = self.session.query(*cols).filter(self.entity\
            .__table__.c.id_file==id).all()
        return q or None

    def create_member(self, data):
        # NOTE: Create new coming files! By John Doe

        member = self.entity(**data)
        self.session.add(member)

        # NOTE: Now commits and closes session in the view instead of here
        # flush() pushes operations to DB's buffer - DCarv
        self.session.flush()
        self.session.commit()

        return member

    def member_to_dict(self, member, fields=None):
        if not isinstance(member, KeyedTuple):
            member = self.member2KeyedTuple(member)

        dict_member = member._asdict()

        fields = getattr(self,'_query', {}).get('select')
        if fields and not '*' in fields:
            if 'download' in fields:
                id_file = dict_member['id_file']
                dict_member['download'] = self.download_url(id_file)
            return {field: dict_member[field] for field in fields}

        elif not 'file' in dict_member:
            id_file = dict_member['id_file']
            dict_member['download'] = self.download_url(id_file)

        return dict_member

    def download_url(self, pk):
        path_split = self.request.path_url.split('/')
        if path_split[len(path_split) -1 ] == str(pk):
            complete = '/download'
        else:
            complete = '/' + str(pk) + '/download'
        return self.request.path_url + complete

    def get_json_obj(self, value, fields, wrap):
        if fields is None:
            fields = self.default_fields
        if not isinstance(value, Iterable):
            value = [value]
        obj = [self.member_to_dict(m, fields) for m in value]
        if wrap:
            obj = self.wrap_json_obj(obj)
        return obj

    def get_raw_member(self, id):
        return self.session.query(self.entity).filter(
            self.entity.__table__.c.id_file == id
        ).first()

    def delete_member(self, id):
        """ 
        @param id: primary key (int) of document.

        Delete a "file type" record. Normally these records are linked
        to "doc type" records. However, there are cases where these
        records ("file type") are not associated with any "doc type",
        so we've used this method to delete them.
        """
        if isinstance(id, int):
            # NOTE: Quando a operação DELETE envolve id_doc! By John Doe

            stmt = delete(self.entity.__table__).where(
                self.entity.__table__.c.id_doc == id)
        else:
            # NOTE: Quando a operação DELETE envolve id_file! By John Doe

            stmt = delete(self.entity.__table__).where(
                self.entity.__table__.c.id_file == id)

        self.session.execute(stmt)

        # NOTE: Now commits and closes session in the view instead of here
        # flush() pushes operations to DB's buffer - DCarv
        self.session.flush()

        # NOTE: Clear cache! By John Doe
        cache.clear_collection_cache(self.base_name)
        return True

