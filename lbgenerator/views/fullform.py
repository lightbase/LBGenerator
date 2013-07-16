from pyramid.view import view_config
import lbgenerator
from lbgenerator import lib
from lbgenerator.lib import generator
from lbgenerator.lib import formgenerator
from lbgenerator.lib import form_op
from lbgenerator.lib import model
from lbgenerator.lib import data_op
from liblightbase.lbbase import xml
from sqlalchemy import create_engine
from xml.dom.minidom import parseString
from pyramid.httpexceptions import HTTPFound
import xmltodict, json
import cgi
from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker, object_mapper

'''@view_config(route_name='full_form', renderer='../templates/fullform/new.pt')
def my_view(request):
    """ Cria o formulário do registro e depois redireciona para acessá-lo.
    """
    #/base/{base_name}/form/full

    params = request.params
    base_name = request.matchdict.get("base_name")
    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    base = session.query(model.LB_bases).filter(model.LB_bases.nome_base == base_name).first()
    if not base:
        return {'form': 'Esta base ainda não existe!'}

    base_id = base.id_base
    base_name = base.nome_base
    base_xml = base.xml_base

    if params:
        #for param in params:
        #    print(param)

        files = [(param.split('.')[len(param.split('.'))-1], params.get(param))
                for param in params
                if isinstance(params.get(param), cgi.FieldStorage)]

        if not engine.dialect.has_table(session, 'lb_regs_%s' %(base_name)):
            metadata.create_all(tables=[regs_table])
        if files and not engine.dialect.has_table(session, 'lb_docs_%s' %(base_name)):
            metadata.create_all(tables=[docs_table])

        regs_nextval = session.execute(model.Regs_seq(base_name).seq)

        docs = [{'tagname':tagname,
                    'id_doc':str(session.execute(model.Docs_seq(base_name).seq)),
                    'filename': file.filename,
                    'blob': file.file.read(),
                    'mimetype': file.type}
                    for tagname, file in files]

        reg_xml =  form_op.get_xml(base_xml, params, regs_nextval, docs)

        reg_data = {'id_reg': regs_nextval,
                    'reg_xml': reg_xml,
                    'reg_json': json.dumps(xmltodict.parse(reg_xml)),
                    'docs': docs
                   }

        reg_id = data_op.save_reg(base_name, reg_data)
        location = 'http://neo.lightbase.cc/lb/%s/form/full/%s' %(base_name, reg_id)

        return HTTPFound(location=location)

    if not engine.dialect.has_table(session, 'lb_forms'):
        metadata.create_all(tables=[forms_table])
    form = session.query(model.LB_forms.html_form).filter(model.LB_forms.id_base == base_id,
                                                         model.LB_forms.nome_form == 'full').first()
    if form: form = form[0]
    else:
        doc = parseString(base_xml)
        base = xml.xml_to_base(doc)
        form = formgenerator.generate_form(base)

        form_data = {'base_id': base_id,
                     'form_name': 'full',
                     'form_xml': '<form_xml/>',
                     'form_html': form
                    }

        data_op.save_form(base_name, form_data)

    session.close()

    return {'form': form}


@view_config(route_name='access_registry', renderer='../templates/fullform/access.pt')
def my_view2(request):

    #/lb/{base_name}/form/full/{id_reg}
    base_name = request.matchdict.get('base_name')
    id_reg = request.matchdict.get('id_reg')

    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)

    base_name = session.query(model.LB_bases.nome_base).filter(model.LB_bases.nome_base == base_name).first()

    if base_name and engine.dialect.has_table(session, 'lb_regs_%s' %(base_name)):

        Regs = model.map_class_to_table(model.LB_regs, regs_table, 'Regs')
        reg = session.query(Regs).filter(Regs.id_reg == id_reg).first()

        if reg: response = reg.id_reg, reg.xml_reg, reg.json_reg
        else: response = 'Este registro ainda não foi criado!'

    else:
        response = 'Esta base/registro ainda não foi criado!'

    session.close()
    return {'response': response}'''









