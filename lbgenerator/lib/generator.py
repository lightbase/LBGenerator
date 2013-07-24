
import liblightbase
from liblightbase import lbtypes, lbmetaclass, lbxml
import liblightbase.lbbase
from liblightbase.lbbase import Base
from liblightbase.lbbase.campos import CampoObjeto, Campo, Indice, Tipo, Multi
from liblightbase.lbbase.xml import base_to_xml, xml_to_base
#from lbgenerator.lib import elastics
from lbgenerator.lib import formgenerator
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

class BaseContextObject():

    """ Provides lbbase.Base Objects 
    """
    def __init__(self, session, entity):
        self.session = session
        self.entity = entity
        self.bases = dict()

    def schema(self, base_name):
        schema = dict()
        obj = self.get_base(self.base_name)['obj']
        for i in obj.objeto.objeto:
            if hasattr(i, 'objeto'): schema.update({i.nome: [str]})
            else: schema.update({i.nome: str})
        return schema

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
        #print(self.bases[base_name]['schema'])
        return self.bases[base_name]

    def set_base_schema(self, base_obj):
        obj_schema = dict()
        for obj in base_obj.objeto.objeto:
            if hasattr(obj, 'multivalued'):
                if len(obj.objeto.objeto) == 1:
                    obj_schema[obj.nome] = [str]
            else:
                obj_schema[obj.nome] = str
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


class LBGenerator():

    def validate_form(self,params):
        """
        Receives a NestedMultiDict with the params of the form and validate it.
        Return valid or invalid
        """
        validation = True
        #verify if there are empty values at params:
        for param in params:
            if (params.get(param) == '') or (params.get(param) is None) :
                validation = False
            if params.get(param).find(']]>') >= 0 :
                validation = False
            if params.get(param).find('%') >= 0 :
                validation = False

        #TODO:verify if there is at least one field on base.

        return validation


    def parse_campo(self,field):
        """
        Receives values of variables of a field element within a string format
        return a Campo object type
        """

        campos_dict2 = dict()
        field2 = dict()

        for elm2 in field:
            antes, separador, depois = elm2.partition('objeto.campo.')

            if separador:
                numero, ponto, atributo = depois.partition('.')

                if campos_dict2.get(numero):
                    campos_dict2[numero][atributo] = field.get(elm2)
                else:
                    campos_dict2[numero] = dict()
                    campos_dict2[numero][atributo] = field.get(elm2)

            elif elm2 == 'tipo':
                if field.get(elm2) == '':
                    tipo = None
                    field2[elm2] = tipo
                elif not isinstance(field.get(elm2), Tipo):
                    tipo = Tipo(tipo = field.get(elm2))
                    field2[elm2] = tipo

            elif elm2 == 'indice':
                indices = []
                for i in field.get(elm2):
                    indice = Indice(indice=i)
                    indices.append(indice)
                field2['indexacao'] = indices

            elif elm2 == 'multi':
                multilist = []
                for m in field.get(elm2):
                    multi = Multi(multi=m)
                    multilist.append(multi)
                field2['multi'] = multilist

            else:
                field2[elm2] = field.get(elm2)

        objeto_list = list()
        for campo2 in campos_dict2:
            campo_obj2 = self.parse_campo(campos_dict2[campo2])
            objeto_list.append(campo_obj2)

        if len(objeto_list) > 0:
            objeto = CampoObjeto(objeto=objeto_list)
            field2['objeto'] = objeto

        campo_obj3 = Campo(**field2)
        return campo_obj3


    def create_base(self,vars):
        """ 
        Get params and generate a Base object for creating xml
        return Base object type
        """

        nome_base = vars.get('base.nome')
        descricao_base = vars.get('base.descricao')
        senha_base = vars.get('base.senha')
        exportar_indice = vars.get('base.exportar_indice')
        url_indice = vars.get('base.url_indice')
        tempo_indice = vars.get('base.tempo_indice')
        extrair_doc = vars.get('base.extrair_doc')
        tempo_extrator = vars.get('base.tempo_extrator')

        campos_dict = dict()
        for elm in vars.keys():

            base_attrs = elm == 'base.nome' or elm == 'base.descricao' or elm == 'base.senha' or \
                elm == 'base.exportar_indice' or elm == 'base.url_indice' or elm == 'base.tempo_indice' or \
                elm == 'base.extrair_doc' or elm == 'base.tempo_extrator'
            if base_attrs:
                continue

            antes, separador, depois = elm.partition('.objeto.campo.')

            if separador:
                numero, ponto, atributo = depois.partition('.')

                if campos_dict.get(numero):

                    if atributo.find('indice') != -1 or atributo.find('multi') != -1:
                        campos_dict[numero][atributo] = vars.getall(elm)
                    else:
                        campos_dict[numero][atributo] = vars.get(elm)
                else:

                    campos_dict[numero] = dict()
                    if atributo.find('indice') != -1 or atributo.find('multi') != -1:
                        campos_dict[numero][atributo] = vars.getall(elm)
                    else:
                        campos_dict[numero][atributo] = vars.get(elm)

        objeto_elm2 = list()

        for campo in campos_dict:

            campo_obj = self.parse_campo(campos_dict[campo])
            objeto_elm2.append(campo_obj)

        objeto = CampoObjeto(objeto=objeto_elm2)

        base = Base(
          nome = nome_base,
          descricao = descricao_base,
          senha = senha_base,
          exportar_indice = exportar_indice,
          url_indice = url_indice,
          tempo_indice = tempo_indice,
          extrair_doc = extrair_doc,
          tempo_extrator = tempo_extrator,
          objeto = objeto
          )

        return base

    def parse_request(self,params):
        #es = elastics.ESConnector()

        base = self.create_base(params)
        basexml = base_to_xml(base)

        doc = parseString(basexml)
        children = doc.firstChild.childNodes
        base_name = '#text'
        for child in children:
            if child.nodeName == 'nome':
                base_name = child.firstChild.nodeValue

        #basejson = base_to_json(base)

        #insert object in database
        #self.save_base_row(basexml,tbl)

        #index object on elasticsearch
        #es_obj = es.xml_to_json(basexml)
        #json_to_base(es_obj)
        #es.index(es_obj,'doc_type',self.counter,index='index')

        #make form
        #form = formgenerator.generate_form(base)
        #print(basexml)
        #print(form)

        return base, base_name, bytes.decode(basexml)



