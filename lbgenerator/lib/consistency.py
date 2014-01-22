
from lbgenerator.model import begin_session
from lbgenerator.model import doc_hyper_class
from lbgenerator.lib import utils
from pyramid.decorator import reify
import json

class Consistency():

    def __init__(self, base, registry):
        self.base = base
        self.registry = utils.to_json(registry)

    @reify
    def session(self):
        return begin_session()

    def normalize(self):
        """
        This method sincronizes database doc objecs and doc fields within json_reg.
        The main purpose is when user removes a file from registry, this method will
        delete the file on database. If the reverse way happens (the file doesnt exists 
        on database but exists in registry) , this method will delete the field from
        registry. The case must be studied.
        """
        self.entity = doc_hyper_class(self.base.name)
        self.files = self.session.query(self.entity.id_doc).filter_by(id_reg=self.registry['id_reg']).all()
        # self.files = [(1,), (2,) ... ]

        # Remove all files in registry that are not in database
        self.registry = self.remove_inconsistent_files(self.registry)

        # Delete all files in database that are not in registry
        for (id,) in self.files:
            self.session.query(self.entity).filter_by(id_doc=id).delete()

        self.session.commit()
        self.session.close()

        return json.dumps(self.registry, ensure_ascii=False)

    def remove_inconsistent_files(self, registry):

        #TODO: Test this function

        if type(registry) is dict:
            _registry = registry.copy()

        elif type(registry) is list:
            _registry = {registry.index(i): i for i in registry}

        to_delete = [ ]
        for k, v in _registry.items():

            if type(v) is dict and utils.is_file_mask(v):
                id = v['id_doc']
                if not (id,) in self.files:
                    # file is not in database, delete it from registry
                    to_delete.append(k)
                else:
                    # file is OK, remove it from list
                    self.files.remove((id,))

            elif type(v) is dict or type(v) is list:
                registry[k] = self.remove_inconsistent_files(v)

        to_delete.reverse()
        for k in to_delete:
            # DANGEROUS !!!!!
            # When will it happen ???
            # execute, or not to execute ???
            pass
            # del registry[k]

        return registry
