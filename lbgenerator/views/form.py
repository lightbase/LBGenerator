from pyramid.view import view_config
from pyramid.response import Response
from lbgenerator.lib import model
from lbgenerator.lib import data_op
from lbgenerator.lib import xhandler
from lbgenerator.lib import form_op
from sqlalchemy import *
from sqlalchemy.orm import *
from xml.dom.minidom import parseString
from pyramid.httpexceptions import HTTPFound
import ast
import xmltodict, json
import cgi

@view_config(route_name='new_form', renderer='../templates/form/new.pt')
def my_view1(request):

    #/lb/{base_name}/form/new
    base_name = request.matchdict.get("base_name")
    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    params = request.params
    if params:

        form_html = params.get('form_html')
        form_name = params.get('form_name')
        containers_ct = params.get('containers_counter')
        items_backup = ast.literal_eval(params.get('items_backup'))

        containers_input = '<input id="containers_ct" type="hidden" value="%s">' %(containers_ct)
        items_input = '<input id="items_backup" type="hidden" value="%s">' %(items_backup)

        form_html += containers_input + items_input
        base_id = session.query(model.LB_bases.id_base).filter(model.LB_bases.nome_base == base_name).first()

        form_data = {'base_id': base_id,
                     'form_name': form_name,
                     'form_xml': '<xmlform/>',
                     'form_html': form_html
                    }

        data_op.save_form(base_name, form_data)

        location = 'http://neo.lightbase.cc/lb/%s/reg/%s/new' %(base_name, form_name)
        return HTTPFound(location=location)

    if not engine.dialect.has_table(session, 'lb_bases'):
        metadata.create_all(tables=[bases_table])

    base_xml = session.query(model.LB_bases.xml_base).filter(model.LB_bases.nome_base == base_name).first()

    if not base_xml:
        return {'grid': '', 'items': ''}

    grid, items = xhandler.get_xdata(base_xml[0])

    session.close()

    return {'grid': grid, 'items': items}

@view_config(route_name='edit_form', renderer='../templates/form/edit.pt')
def my_view2(request):

    #/lb/{base_name}/form/{form_name}/edit
    return {'project':'LBGenerator','matchdict':request.matchdict}

@view_config(route_name='delete_form', renderer='../templates/form/delete.pt')
def my_view3(request):

    #/lb/{base_name}/form/{form_name}/delete
    return {'project':'LBGenerator','matchdict':request.matchdict}
