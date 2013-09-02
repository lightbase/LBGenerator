
from liblightbase.lbbase import Base
from liblightbase.lbbase.genesis import json_to_base

class BaseContextObject():

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
            base_xml = session.query(self.entity.xml_base).filter_by(nome_base=base_name).first()
            session.close()
            if not base_xml:
                raise Exception('Base "%s" does not exist' %(base_name))
            return self.set_base_up(base_name, base_xml[0])
        return base

    def set_base_up(self, base_name, base_xml):
        base_obj = self.set_base_obj(base_xml)
        base_cc = self.set_base_cc(base_name, base_obj)
        base_schema = self.set_base_schema(base_obj)
        self.bases[base_name] = dict(
            obj = base_obj,
            cc = base_cc,
            schema = base_schema
        )
        return self.bases[base_name]

    def set_base_schema(self, base_obj):
        obj_schema = dict()
        def generic_type():
            return lambda v: v
        for obj in base_obj.objeto.objeto:
            if hasattr(obj, 'multivalued'):
                if len(obj.objeto.objeto) == 1:
                    obj_schema[obj.nome] = [generic_type()]
            else:
                obj_schema[obj.nome] = generic_type()
        obj_schema['id_reg'] = generic_type()
        return obj_schema

    def set_base_obj(self, base_xml):
        try:
            base = xml_to_base(parseString(base_xml))
        except ExpatError:
            raise Exception('Malformed XML data')
        return base

    def set_base_cc(self, base_name, base_obj):
        base_cc = dict(
            normal_cols = list(),
            unique_cols = list(),
            date_types = list(),
            Textual = list(),
            SemIndice = list()
        )
        for obj in base_obj.objeto._objeto:
            fname = obj.nome
            if hasattr(obj, 'indexacao'):
                for index in obj.indexacao:
                    if index.indice in ['Ordenado', 'Vazio']:
                        base_cc['normal_cols'].append(fname)
                    if index.indice in ['Unico']:
                        base_cc['unique_cols'].append(fname)
                    if index.indice in ['Textual']:
                        base_cc['Textual'].append(fname)
                    if index.indice in ['SemIndice']:
                        base_cc['SemIndice'].append(fname)
            if hasattr(obj, 'tipo'):
                if obj.tipo._tipo == 'Data':
                    base_cc['date_types'].append(fname)
        return base_cc



