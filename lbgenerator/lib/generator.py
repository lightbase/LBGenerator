
from . import utils
from liblightbase.lbbase.genesis import json_to_base

class BaseMemory():

    """ Provides lbbase.Base Objects 
    """
    def __init__(self, session, entity):
        self.session = session
        self.entity = entity
        self.bases = dict()

    def get_base(self, base_name):
        base = self.bases.get(base_name)
        if base is None:
            session = self.session()
            base_json = session.query(self.entity.struct).filter_by(name=base_name).first()
            session.close()
            if not base_json:
                raise Exception('Base "%s" does not exist' %(base_name))
            return self.set_base(utils.json2object(base_json[0]))
        return base

    def set_base(self, base_json):
        base = json_to_base(base_json)
        self.bases[base.name] = base
        return base




