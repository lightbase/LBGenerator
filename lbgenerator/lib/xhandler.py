
from xml.dom.minidom import parseString

def get_xtype(lbtype):
    """ Returns current ExtJS4 xtype and vtype for each lbtype defined.
    """
    vtype = None

    xdict = {
            'AlfaNumerico': ('textfield', 'alphanum'),
            'Documento': ('filefield', vtype),
            'Imagem':('filefield', vtype),
            'Som': ('filefield', vtype),
            'Video': ('filefield', vtype),
            'Arquivo': ('filefield', vtype),
            'Inteiro': ('numberfield', vtype),
            'AutoEnumerado': ('numberfield', vtype),
            'Decimal': ('textfield', 'alphanum'),
            'Data': ('datefield', vtype),
            'Hora': ('timefield', vtype),
            'URL': ('textfield', 'url'),
            'Verdadeiro/Falso': ('textfield', vtype),
            'Texto': ('textfield', vtype),
            'HTML': ('htmleditor', vtype),
            'Email': ('textfield', 'email')
    }

    if lbtype in xdict:
        return xdict.get(lbtype)
    else:
        raise KeyError('lbtype is not a valid one. Instead it is: %s' %(lbtype))

def get_buttons(field_name):

    plus = {'id': '%s-plus' %(field_name),
            'xtype': 'button',
            'text': '+',
            'handler': 'function(){addFieldSet()}'}

    minus = {'id': '%s-minus' %(field_name),
             'xtype': 'button',
             'text': '-',
             'handler': 'funtion(){removeFieldSet()}'}

    return plus, minus

def get_xjson(elm):
    """ Returns items json object string for rendering the new form.
    """
    subitems = list()
    items_dic = dict()

    items_dic['xtype'] = 'fieldset'
    items_dic['items'] = list()
    items_dic['width'] = 400

    field_count = 0
    group_count = 0
    for field in elm.childNodes:
        if field.nodeName == 'campo':
            field_count += 1
        if field.nodeName == 'grupo':
            group_count +=1
        if field.nodeName == 'nome':
            field_name = field.firstChild.nodeValue

    plusbutton, minusbutton = get_buttons(field_name)

    child_len = len(elm.childNodes)
    ct = 0

    for field in elm.childNodes:
        ct = ct + 1
        if field.nodeName == 'descricao':
            #items_dic['title'] = field.firstChild.nodeValue
            items_dic['fieldLabel'] = field.firstChild.nodeValue

        elif field.nodeName == 'nome':
            # conflito de ids quando multivalorado simples 
            # solução : addicionar '-grupo'
            items_dic['id'] = field.firstChild.nodeValue + '-grupo'
            items_dic['name'] = field.firstChild.nodeValue
            items_dic['title'] = field.firstChild.nodeValue

        elif field.nodeName == 'tipo' and not elm.getAttribute('multivalued'):
            xtype, vtype = get_xtype(field.firstChild.nodeValue)
            items_dic['xtype'] = xtype
            if vtype: items_dic['vtype'] = vtype

        elif field.nodeName == 'campo':
            sub_dic = dict()
            for field_elm in field.childNodes:
                if field_elm.nodeName == 'nome':
                    sub_dic['name'] = field_elm.firstChild.nodeValue
                    sub_dic['id'] = field_elm.firstChild.nodeValue
                    sub_plus, sub_minus = get_buttons(field_elm.firstChild.nodeValue)
                if field_elm.nodeName == 'descricao':
                    sub_dic['fieldLabel'] = field_elm.firstChild.nodeValue
                if field_elm.nodeName == 'tipo':
                    xtype, vtype = get_xtype(field_elm.firstChild.nodeValue)
                    sub_dic['xtype'] = xtype
                    if vtype: sub_dic['vtype'] = vtype

            items_dic['items'].append(sub_dic)

            if field_count == 1 and group_count == 0:
                pass
                #items_dic['items'].append(sub_plus)
                #items_dic['items'].append(sub_minus)


        elif field.nodeName == 'grupo':
            items_dic['items'].append(get_xjson(field))


        if not plusbutton in items_dic['items'] and ct == child_len:# put buttons at the end 
            items_dic['items'].append(plusbutton)
            items_dic['items'].append(minusbutton)

    return items_dic


def get_xgrid(base_xml):
    """ Return json data to build the custom form grid panel.
    """

    base_doc = parseString(base_xml)
    bigG = [child for child in base_doc.firstChild.childNodes if child.nodeName == 'grupo'][0]

    grid = list()
    lb_elms = list()

    for fields in bigG.childNodes:
        row = {}

        if fields.nodeName == 'grupo' or  fields.nodeName == 'campo':
            lb_elms.append(fields)

            row['tipo'] = '#tipo'
            for fields_attr in fields.childNodes:

                if fields_attr.nodeName == 'campo':
                    row['tipo'] = 'Grupo'

                elif fields_attr.firstChild.nodeValue is not None:

                    if fields_attr.nodeName == 'tipo' and row['tipo'] == 'Grupo':
                        continue
                    else:
                        row[fields_attr.nodeName] = fields_attr.firstChild.nodeValue

            grid.append(row)

    return grid, lb_elms

def get_xdata(base_xml):

    grid, lb_elms = get_xgrid(base_xml)

    items = []
    for elm in lb_elms:
        items.append(get_xjson(elm))

    return grid, items

