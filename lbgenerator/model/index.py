
import copy
from .. import config
from ..lib import utils
import requests, datetime
from requests.exceptions import Timeout

class CreatedIndex():
    """ Represents a successfull response when creating an index.
    """
    def __init__(self, created, _index, _type, _id, _version):
        pass

class UpdatedIndex():
    """ Represents a successfull response when updating an index.
    """
    def __init__(self, created, _index, _type, _id, _version):
        pass

class DeletedIndex():
    """ Represents a successfull response when deleting an index.
    """
    def __init__(self, found, _index, _type, _id, _version):
        pass

class DeletedRoot():
    """ Represents a successfull response when deleting root index.
    """
    def __init__(self, acknowledged, ok):
        pass

class Index():

    """ Handles document index
    """
    def __init__(self, base, get_full_document):
        self.base = base
        self.get_full_document = get_full_document
        self.is_indexable = self.base.metadata.idx_exp
        self.INDEX_URL = self.base.metadata.idx_exp_url
        if self.is_indexable:
            self._host = self.INDEX_URL.split('/')[2]
            self._index = self.INDEX_URL.split('/')[3]
            self._type = self.INDEX_URL.split('/')[4]
        self.TIMEOUT = config.REQUESTS_TIMEOUT

    def to_url(self, *args):
        return '/'.join(list(args))

    def is_created(self, msg):
        """ Ensures index is created
        """
        try: CreatedIndex(**msg); return True
        except: return False

    def is_updated(self, msg):
        """ Ensures index is updated
        """
        try: UpdatedIndex(**msg); return True
        except: return False

    def is_deleted(self, msg):
        """ Ensures index is deleted
        """
        try: DeletedIndex(**msg); return True
        except: return False

    def is_root_deleted(self, msg):
        """ Ensures root index is deleted
        """
        try: DeletedRoot(**msg); return True
        except: return False

    def create(self, data):
        """ Creates index 
        """
        if not self.is_indexable:
            return False, data

        document = utils.object2json(data['document'], ensure_ascii=True)

        # Try to index document
        url = self.to_url(self.INDEX_URL, str(data['id_doc']))
        try:
            response = requests.post(url,
                data=document,
                timeout=self.TIMEOUT).json()
        except:
            response = None

        if self.is_created(response):
            data['dt_idx'] = datetime.datetime.now()
        else:
            data['dt_idx'] = None
            return False, data

        self.sync_metadata(data) # Syncronize document metadata.
        return True, data

    def update(self, id, data, session):
        """ Updates index 
        """
        if not self.is_indexable:
            return False, data

        document_copy = copy.deepcopy(data['document'])

        # Get full document
        full_document = self.get_full_document(document_copy, session)

        # IMPORTANT: This time we dont have ensure_ascii=False
        document = utils.object2json(full_document, ensure_ascii=True)
        url = self.to_url(self.INDEX_URL, str(data['id_doc']))

        try:
            response = requests.put(url,
                data=document,
                timeout=self.TIMEOUT).json()
        except:
            response = None

        if self.is_updated(response):
            data['dt_idx'] = datetime.datetime.now()
        else:
            data['dt_idx'] = None

        self.sync_metadata(data) # Syncronize document metadata.
        return True, data

    def delete(self, id):
        """ Deletes index 
        """
        if not self.is_indexable:
            # index does not exist, error = false
            return False, None

        url = self.to_url(self.INDEX_URL, str(id))

        try:
            response = requests.delete(url, timeout=self.TIMEOUT)
        except Exception as e:
            response = None
            msg_error = str(e)
        else:
            msg_error = response.text

        try:
            response = response.json()
        except Exception as e:
            response = None

        if self.is_deleted(response):
            # index is deleted, error = false 
            return False, None
        else:
            # index is not deleted, error = true 
            data = dict(
                base = self.base.metadata.name,
                id_doc = id,
                dt_error = datetime.datetime.now(),
                msg_error = msg_error)

            return True, data

    def delete_root(self):
        """ Deletes root type
        """
        try: response = requests.delete(self.INDEX_URL, timeout=self.TIMEOUT).json()
        except : response = None

        if self.is_root_deleted(response):
            response = True
        else:
            response = False
        return response

    def sync_metadata(self, data):
        data['document']['_metadata']['dt_idx'] = data\
            .get('dt_idx', None)

