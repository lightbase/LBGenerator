import requests, datetime, json
from lbgenerator.lib import utils
from lbgenerator import config

class CreatedIndex():
    """ Represents a successfull response when creating an index.
    """
    def __init__(self, ok, _index, _type, _id, _version):
        pass

class UpdatedIndex():
    """ Represents a successfull response when updating an index.
    """
    def __init__(self, ok, _index, _type, _id, _version):
        pass

class DeletedIndex():
    """ Represents a successfull response when deleting an index.
    """
    def __init__(self, ok, found, _index, _type, _id, _version):
        pass

class DeletedRoot():
    """ Represents a successfull response when deleting root index.
    """
    def __init__(self, acknowledged, ok):
        pass

class Index():

    """ Handles registry index
    """
    def __init__(self, base, get_full_reg):
        self.base = base
        self.get_full_reg = get_full_reg
        self.is_indexable = self.base.index_export
        self.INDEX_URL = self.base.index_url
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
            return data

        # Get parsed registry
        registry = utils.to_json(data['json_reg'])
        #parser = RegistryParser(self.base.object, registry)
        # IMPORTANT: This time we dont have ensure_ascii=False
        #registry = json.dumps(parser.parse(), ensure_ascii=False)
        #registry = json.dumps(parser.parse())
        registry = json.dumps(registry)

        # Try to index registry
        url = self.to_url(self.INDEX_URL, str(data['id_reg']))
        try: response = requests.post(url, data=registry, timeout=self.TIMEOUT).json()
        except: response = None

        if self.is_created(response):
            data['dt_index_tex'] = datetime.datetime.now()
        else:
            data['dt_index_tex'] = None
        return data

    def update(self, id, data):
        """ Updates index 
        """
        if not self.is_indexable:
            return data

        # Get full registry
        full_reg = self.get_full_reg(utils.to_json(data['json_reg']), close_session=False)
        # Get parsed registry
        #parser = RegistryParser(self.base.object, full_reg)
        # registry = json.dumps(parser.parse(), ensure_ascii=False)
        # IMPORTANT: This time we dont have ensure_ascii=False
        #registry = json.dumps(parser.parse())
        registry = json.dumps(full_reg)

        # Try to index registry
        url = self.to_url(self.INDEX_URL, str(id))
        try: response = requests.put(url, data=registry, timeout=self.TIMEOUT).json()
        except: response = None

        if self.is_updated(response):
            data['dt_index_tex'] = datetime.datetime.now()
        else:
            data['dt_index_tex'] = None
        return data

    def delete(self, id):
        """ Deletes index 
        """
        if not self.is_indexable:
            return True

        url = self.to_url(self.INDEX_URL, str(id))
        try: response = requests.delete(url, timeout=self.TIMEOUT).json()
        except : response = None

        if self.is_deleted(response):
            response = True
        else:
            response = False
        return response

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

class RegistryParser():

    def __init__(self, base, registry):
        self.base = base
        self.registry = registry
        self.id = self.registry['id_reg']
        del self.registry['id_reg']

    def get_base(self, base, attr):
        for content in base['content']:
            if content.get('field'):
                field = content['field']
                if field['name'] == attr:
                    return field
            elif content.get('group'):
                group = content['group']
                if group['metadata']['name'] == attr:
                    return group
        raise Exception('Structure "%s" is not present in base definitions.' % attr)

    def destroy_field(self, base, registry, field):
        if 'Nenhum' in base.get('indices', []):
            del registry[field]
            return True
        return False

    def parse(self, base=None, registry=None):
        """ Will search fields in registry that are setted with "NoIndex" in base structure, 
            and then will delete it from registry, so they cannot be indexed.
        """
        if not registry: registry = self.registry
        if not base: base = self.base

        _registry = registry.copy()

        for attr in _registry:

            value = _registry[attr]
            _base = self.get_base(base, attr)

            #is_field = isinstance(_base, Field)
            #is_group = isinstance(_base, Group)

            if type(value) is dict and not 'id_doc' in value:
                self.parse(_base, value)

            elif type(value) is list:

                if not self.destroy_field(_base, registry, attr):
                    for item in value:
                        if type(item) is dict:
                            self.parse(_base, item)
            else:
                self.destroy_field(_base, registry, attr)

        self.registry['id_reg'] = self.id
        return self.registry
