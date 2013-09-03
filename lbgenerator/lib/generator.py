
from liblightbase.lbbase import Base
from liblightbase.lbbase.genesis import json_to_base
from lbgenerator.lib import utils

class BaseMemory():

    """ Provides lbbase.Base Objects 
    """
    def __init__(self, session, entity):
        self.session = session
        self.entity = entity
        self.bases = dict()

    def get_base(self, base_name):
        base = self.bases.get(base_name)
        session = self.session()
        if base is None:
            base_json = session.query(self.entity.json_base).filter_by(nome_base=base_name).first()
            session.close()
            if not base_json:
                raise Exception('Base "%s" does not exist' %(base_name))
            return self.set_base_up(utils.to_json(base_json[0]))
        return base

    def set_base_up(self, base_json):
        base = json_to_base(base_json)
        self.set_base_cc(base)
        self.bases[base.name] = base
        return base

    def set_base_cc(self, base):
        base_cc = dict(
            normal_cols = list(),
            unique_cols = list(),
            date_types = list(),
            Textual = list(),
        )
        for element in base.content:
            fname = element.name
            indices = getattr(element, 'indices', None)
            datatype = getattr(element, 'datatype', None)
            if indices:
                for index in element.indices:
                    if index.index in ['Ordenado', 'Vazio']:
                        base_cc['normal_cols'].append(fname)
                    if index.index in ['Unico']:
                        base_cc['unique_cols'].append(fname)
                    if index.index in ['Textual']:
                        base_cc['Textual'].append(fname)
            if datatype:
                if datatype.datatype == 'Data':
                    base_cc['date_types'].append(fname)

        base.custom_columns = base_cc



