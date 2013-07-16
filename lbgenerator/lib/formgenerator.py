from xml.dom import minidom
from liblightbase.lbbase import Base
from liblightbase.lbbase import campos

def generate_form(base):
    """
    Convert Base object to HTML form structure 
    Receives an lbbase Base object
    """
    # create XML document
    doc = minidom.Document()

    form = doc.createElement('form')
    form.setAttribute('name','full')
    form.setAttribute('method','post')
    form.setAttribute('enctype','multipart/form-data')

    def create_campo(doc, field):
        """Here we create fields to fill the form.
        """
        if isinstance(field, campos.Campo):
            div = doc.createElement('div')

            multi = False
            if 'multivalued' in field.__dict__.keys():
                multi = True

            tipo = field.__dict__.get('_tipo')
            if tipo:
                tipo = tipo.tipo

                text_types = ['AlfaNumerico', 'Texto', 'Hora', 'Decimal',
                'Moeda', 'AutoEnumerado', 'Verdadeiro/Falso', 'HTML']

                file_types = ['Arquivo', 'Documento', 'Imagem', 'Video', 'Som']

                if tipo in text_types:
                    input_type = 'text'
                elif tipo in file_types:
                    input_type = 'file'
                elif tipo == 'URL':
                    input_type = 'url'
                elif tipo == 'Inteiro':
                    input_type = 'number'
                elif tipo == 'Data' :
                    input_type = 'date'
                elif tipo == 'Email' :
                    input_type = 'email'

            for value in field.__dict__.keys():
                if isinstance(field.__dict__.get(value), campos.Tipo):
                    continue
                elif value == '_indexacao':
                    continue

                elif value == 'multivalued':
                    ipt = doc.createElement('input')
                    ipt.setAttribute('type','hidden')
                    #if isinstance(field.__dict__.get(value)[0],campos.Multi):
                    #    ipt.setAttribute('value','multi')
                    ipt.setAttribute('value','multi')
                    div.appendChild(ipt)

                elif value == 'nome':
                    name = doc.createElement('input')
                    name.setAttribute('type','hidden')
                    name.setAttribute('value',field.__dict__.get(value))
                    div.appendChild(name)

                elif value == 'objeto':
                    objeto_2 = field.__dict__.get(value)
                    #if len(objeto_2.objeto) < 2 and multi:
                    #    continue
                    legend2 = doc.createElement('legend')
                    legend2_text = doc.createTextNode('')
                    legend2.appendChild(legend2_text)
                    fieldset = doc.createElement('fieldset')
                    for elm in objeto_2.objeto:
                        campo_2 = create_campo(doc, elm)
                        fieldset.appendChild(legend2)
                        fieldset.appendChild(campo_2)
                else:
                    if value == 'descricao':
                        dl = doc.createElement('dl')
                        dt = doc.createElement('dt')
                        label = doc.createElement('label')
                        label.setAttribute('for',field.__dict__.get(value))
                        label_text = doc.createTextNode(field.__dict__.get(value) + ':')
                        label.appendChild(label_text)
                        dt.appendChild(label)

                        dd = doc.createElement('dd')
                        input_elm = doc.createElement('input')
                        if tipo:
                            input_elm.setAttribute('type',input_type)
                            input_elm.setAttribute('lbtype',tipo)
                        else:
                            input_elm.setAttribute('type','text')
                        input_elm.setAttribute('name',field.__dict__.get(value))
                        dd.appendChild(input_elm)

                        dl.appendChild(dt)
                        dl.appendChild(dd)
                        div.appendChild(dl)

                if 'fieldset' in vars():
                    div.appendChild(fieldset)

            return div
        else:
            raise Exception('TypeError this should be an instance of Campo. Instead it is %s' % campo)

    for elm in base.__dict__.keys():
        if isinstance(base.__dict__.get(elm), campos.CampoObjeto):
            objeto = base.__dict__.get(elm)

    fieldset = doc.createElement('fieldset')
    legend = doc.createElement('legend')
    legend_text = doc.createTextNode('Criar Registro')
    legend.appendChild(legend_text)
    fieldset.appendChild(legend)

    for field in objeto.objeto:
        campo = create_campo(doc, field)
        fieldset.appendChild(campo)

    button1 = doc.createElement('input class="button" type="button" onclick="validateForm()" value="OK"')
    button2 = doc.createElement('input class="button" type="reset" value="Cancel"')
    contador = doc.createElement('input type="hidden" id ="contador" value="0"')
    form.appendChild(fieldset)
    form.appendChild(button1)
    form.appendChild(button2)
    form.appendChild(contador)
    doc.appendChild(form)

    xml = doc.toprettyxml(indent='',newl='',encoding='utf-8')
    xml = bytes.decode(xml)
    form = xml.replace('<?xml version="1.0" encoding="utf-8"?>','')
    return form
