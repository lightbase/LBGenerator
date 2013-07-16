
from pyramid.view import view_config
from lbgenerator.lib import model
from lbgenerator.lib import form_op
from lbgenerator.lib import data_op
from lbgenerator.lib.registry import Registry
from sqlalchemy import *
from sqlalchemy.orm import *
import cgi
import xmltodict, json
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from xml.dom.minidom import parseString

@view_config(route_name='new_reg', renderer='../templates/reg/new.pt')
def my_view1(request):
    #lb/{base_name}/reg/{form_name}/new

    form_name = request.matchdict.get("form_name")
    base_name = request.matchdict.get("base_name")
    engine, session, metadata = model.Engine().get_conn()
    global docs_table
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    base = session.query(model.LB_bases).filter(model.LB_bases.nome_base == base_name).first()

    if not base:
        session.close()
        return {'form': 'Base não existe !'}

    base_id = base.id_base
    base_name = base.nome_base
    base_xml = base.xml_base

    params = request.params
    if params:
        for param in params:
            print(param, params.get(param))

        if not engine.dialect.has_table(session, 'lb_regs_%s' %(base_name)):
            metadata.create_all(tables=[regs_table])

        docs = get_docs(params, base_name, session, engine, metadata)

        regs_nextval = session.execute(model.Regs_seq(base_name).seq)
        reg_xml = form_op.get_xml(base_xml, params, regs_nextval, docs)

        reg_data = {'id_reg': regs_nextval,
                    'reg_xml': reg_xml,
                    'reg_json': json.dumps(xmltodict.parse(reg_xml)),
                    'docs': docs
                   }

        reg_id = data_op.save_reg(base_name, reg_data)
        session.close()
        return Response(json.dumps({'reg_id': reg_id}))

    form_html = session.query(model.LB_forms.html_form).filter(model.LB_forms.nome_form == form_name,
                                                               model.LB_forms.id_base == base_id).first()
    if not form_html:
        session.close()
        return {'form': 'Formulário não existe!'}

    session.close()
    return {'form': form_html[0]}


@view_config(route_name='view_reg', renderer='../templates/reg/view.pt')
def my_view2(request):
    #lb/{base_name}/reg/{form_name}/view/{id_reg}

    response = reg_commons(request)
    return response

@view_config(route_name='edit_reg', renderer='../templates/reg/edit.pt')
def my_view3(request):
    #lb/{base_name}/reg/{form_name}/edit/{id_reg}

    base_name = request.matchdict.get("base_name")
    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    params = request.params
    if params:

        del_files = list()
        for param in params:
            #print(param, params[param])
            if param == 'deleted_file' : del_files.append(params.get(param))

        params = dict(params)
        id_reg = params.pop('reg_id')

        base_xml = session.query(model.LB_bases.xml_base).\
            filter(model.LB_bases.nome_base == base_name).first()[0]

        multis, commons = get_base_groups(base_xml, base_name)

        Regs = model.map_class_to_table(model.LB_regs, regs_table, 'Regs')
        reg = session.query(Regs).filter(Regs.id_reg == id_reg).first()

        reg = Registry(reg.xml_reg, reg.json_reg, multis, commons, del_files)
        reg.set_params()
        reg.set_new_params(params)
        new_params = reg.new_params
        #print('new_params', new_params)

        docs = get_docs(params, base_name, session, engine, metadata)

        reg_xml = form_op.get_xml(base_xml, new_params, id_reg, docs)

        reg_data = {'id_reg': id_reg,
                    'reg_xml': reg_xml,
                    'reg_json': json.dumps(xmltodict.parse(reg_xml)),
                    'docs': docs
                   }

        #reg_id = data_op.update_reg(base_name, reg_data)
        return Response(json.dumps({'reg_id': 'id_reg'}))

    response = reg_commons(request)
    return response

@view_config(route_name='delete_reg', renderer='../templates/reg/delete.pt')
def my_view4(request):
    #lb/{base_name}/reg/{id_reg}/delete
    return {}


def reg_commons(request):

    base_name = request.matchdict.get('base_name')
    id_reg = request.matchdict.get('id_reg')
    form_name = request.matchdict.get('form_name')
    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    base_id = session.query(model.LB_bases.id_base).filter(model.LB_bases.nome_base == base_name).first()

    if not base_id and not engine.dialect.has_table(session, 'lb_regs_%s' %(base_name)):
        session.close()
        return {'response': 'Esta base/registro ainda não foi criado!', 'form': 'null'}

    Regs = model.map_class_to_table(model.LB_regs, regs_table, 'Regs')
    reg = session.query(Regs).filter(Regs.id_reg == id_reg).first()

    form = session.query(model.LB_forms.html_form).filter(model.LB_forms.nome_form == form_name,
                                                          model.LB_forms.id_base == base_id).first()
    if not form:
        session.close()
        return {'response': 'Formulário não existe!', 'form': 'null'}

    if not reg:
        return {'response': 'Este registro ainda não foi criado!', 'form': 'null'}

    response = json.dumps({ "reg_xml": reg.xml_reg, "reg_json": reg.json_reg })

    session.close()
    return {'response': response, 'form': form[0]}

def get_base_groups(base_xml, base_name):

    g_multis = list() 
    s_multis = list()
    commons = list()

    xmldoc = parseString(base_xml)
    groups = xmldoc.getElementsByTagName('grupo')
    for group in groups:
        if group.hasAttribute('multivalued'):
            fields = 0
            for child in group.childNodes:
                if child.nodeName == 'nome':
                    name = child.firstChild.nodeValue
                elif child.nodeName == 'campo':
                    fields += 1
                else: continue
            if fields > 1:
                g_multis.append(name)
            elif fields == 1:
                s_multis.append(name)
        else:
            for child in group.childNodes:
                if child.nodeName == 'nome':
                    name = child.firstChild.nodeValue
                    if name != base_name:
                        commons.append(name)

    return {'single': s_multis, 'group': g_multis}, commons

def get_docs(params, base_name, session, engine, metadata):

    files = [(param.split('.')[len(param.split('.'))-1], params.get(param))
            for param in params
            if isinstance(params.get(param), cgi.FieldStorage)]

    if files and not engine.dialect.has_table(session, 'lb_docs_%s' %(base_name)):
        metadata.create_all(tables=[docs_table])

    docs = [{'tagname': tagname,
             'id_doc': str(session.execute(model.Docs_seq(base_name).seq)),
             'filename': file.filename,
             'blob': file.file.read(),
             'mimetype': file.type }
             for tagname, file in files]

    return docs






