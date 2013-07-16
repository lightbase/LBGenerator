
from xml.dom import minidom
from liblightbase import lbtypes, lbmetaclass, lbxml, lbbase
from liblightbase.lbbase import Base
from liblightbase.lbbase import campos
from liblightbase.lbbase import xml
from xml.dom.minidom import parseString
import cgi

def get_xml(xmlstring, params, regs_nextval, archives):
    """ Build the registry xml
    """

    document = parseString(xmlstring)
    base_attrs = dict([(child.tagName,child.firstChild.nodeValue)
                      for child in document.getElementsByTagName('base')[0].childNodes
                      if child.tagName != 'grupo' or child.tagName != 'senha'])

    base = xml.xml_to_base(document)
    Metaclass, multidict = create_lbmetaclass(base)
    #print(lbxml.class_to_xml(Metaclass))

    object = metaclass_to_object(Metaclass, params, multidict)

    reg_xml = lbxml.object_to_xml(object,
                                  base_attrs=base_attrs,
                                  nextval=regs_nextval,
                                  archives=archives)

    return reg_xml

def create_lbmetaclass(base):
    """ Convert Base object to lbmetaclass object
    """

    def create_class(field, registry, firstiter=False):
        """
        Create lbmetaclass object.
        Return base lbmetaclass object list structure.
        """

        dic = dict()
        if isinstance(field, campos.Campo):

            if 'multivalued' in field.__dict__.keys():

                if len(field.__dict__.get('objeto').__dict__.get('_objeto')) > 1:
                    multigroup.append((field.__dict__.get('nome')))
                else:
                    multisingle.append((field.__dict__.get('nome')))
                multi = True

            else:
                multi = False

            if 'nome' in field.__dict__.keys():
                name = field.__dict__.get('nome')

            if 'objeto' in field.__dict__.keys():
                ob = field.__dict__.get('objeto')
                items = 0
                for o in ob.objeto:
                    items = items + 1
                obj = True
            else:
                obj = False

            for value in field.__dict__.keys():

                if value == 'nome':

                    if firstiter and not obj:
                        dic = {'name':field.__dict__.get(value),
                               'type':'String'}
                    elif not obj:
                        dic[field.__dict__.get(value)] = 'String'

                elif value == 'objeto':

                    li2 = list()
                    objeto_2 = field.__dict__.get('objeto')

                    for elm in objeto_2.objeto:
                        campo_2 = create_class(elm,li2)
                    aux2 = dict()

                    for i2 in campo_2:
                        aux2[next(iter(i2.keys()))] = next(iter(i2.values()))

                    if firstiter:

                        if obj and not multi:
                            dic = {'name':name,
                                   'type':lbtypes.Multiple(aux2)}
                        elif multi:
                            dic = {'name':name,
                                   'type':lbtypes.Array(lbtypes.Multiple(aux2))}
                    else:
                        if obj and not multi:
                            dic[name] = lbtypes.Multiple(aux2)
                        elif multi:
                            dic[name] = lbtypes.Array(lbtypes.Multiple(aux2))
                else:
                    continue

                if not dic in registry:
                    registry.append(dic)
            return registry

        else:
            raise Exception('TypeError this should be an instance of Campo. Instead it is %s' % campo)

    registry = list()
    global multigroup
    multigroup = list()
    global multisingle
    multisingle = list()

    for elm in base.__dict__.keys():
        if isinstance(base.__dict__.get(elm), campos.CampoObjeto):
            objeto = base.__dict__.get(elm)

    for field in objeto.objeto:
        create_class(field, registry, firstiter=True)

    return lbmetaclass.generate_class('Reg', registry), {'single': multisingle, 'group': multigroup}


def metaclass_to_object(Metaclass, params, multidict):
    """ Convert lbmetaclass to lbxml object.
    """

    fields_dict = dict()
    for elm in params.keys():
        bef, sep, aft = elm.partition('.campo.')
        if sep:
            num, point, attr = aft.partition('.')
            if fields_dict.get(num):
                fields_dict[num][attr] = params.get(elm)
            else:
                fields_dict[num] = dict()
                fields_dict[num][attr] = params.get(elm)

    object = Metaclass()

    for field in fields_dict:

        obj = parse_object(fields_dict[field], multidict, firstiter=True)
        firstkey, value = obj.popitem()
        escape = 'object.%s' %(firstkey)

        try: eval(escape).append(value); continue
        except: pass

        try: eval(escape).append({firstkey: value}); continue
        except: pass

        try: object[firstkey] = value
        except: pass


    return object

def parse_object(field, multidict, firstiter=False):
    """ Receive variables values and return json object
    """

    fields_dict = dict()
    field2 = dict()

    multisingle = multidict.get('single')
    multigroup = multidict.get('group')

    for elm in field:
        bef, sep, aft = elm.partition('.campo.')

        if sep:
            num, point, attr = aft.partition('.')

            if fields_dict.get(num):
                if isinstance(field.get(elm), cgi.FieldStorage):
                    fields_dict[num][attr] = field.get(elm).filename
                    continue
                if type(field.get(elm)) is bytes:
                    fields_dict[num][attr] = bytes.decode(field.get(elm))
                    continue

                fields_dict[num][attr] = field.get(elm)
            else:
                fields_dict[num] = dict()
                if isinstance(field.get(elm), cgi.FieldStorage):
                    fields_dict[num][attr] = field.get(elm).filename
                    continue
                if type(field.get(elm)) is bytes:
                    fields_dict[num][attr] = bytes.decode(field.get(elm))
                    continue

                fields_dict[num][attr] = field.get(elm)
        else:
            if isinstance(field.get(elm), cgi.FieldStorage):
                field2[elm] = field.get(elm).filename
                continue
            if type(field.get(elm)) is bytes:
                field2[elm] = bytes.decode(field.get(elm))
                continue

            field2[elm] = field.get(elm)

    obj_list = list()
    obj_dict = dict()

    if not fields_dict:
        return field2

    else:

        for inner_field in fields_dict:
            field_obj = parse_object(fields_dict[inner_field], multidict)
            obj_list.append(field_obj)

        aux_dict = dict()
        for ol in obj_list:

            key, value = ol.popitem()

            if key in multisingle:

                if key in aux_dict:
                    aux_list = aux_dict.get(key)
                    aux_list.append(value)
                    aux_dict[key] = aux_list
                else:
                    if type(value) is dict:
                        aux_dict[key] = [value]
                    else:
                        aux_dict[key] = value

            elif key in multigroup:

                if key in aux_dict:
                    aux_list = aux_dict.get(key)
                    aux_list.append(value)
                    aux_dict[key] = aux_list
                else:
                    aux_dict[key] = [value]

            else:
                aux_dict[key] = value

        key, value = field2.popitem()
        obj_dict[key] = aux_dict

        return obj_dict







