from pyramid.view import view_config
import lbgenerator
#from lbgenerator import lib
from lbgenerator.lib import generator
#from lbgenerator.lib import model
#from lbgenerator.lib import data_op
from pyramid.httpexceptions import HTTPFound
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import *
import urllib.parse
import urllib.request


@view_config(route_name='new_base', renderer='../templates/base/new.pt')
def my_view(request):

    #/lb/new
    params = request.params
    gen = generator.LBGenerator()

    if params:
        valid = gen.validate_form(params)
        if valid:
            base, base_name, base_xml = gen.parse_request(params)

            values = {'nome_base': base_name, 'xml_base': base_xml}
            data = urllib.parse.urlencode(values).encode('utf-8')
            domain = request.route_url('home')
            url = domain + 'api/base'
            req = urllib.request.Request(url, data)
            urllib.request.urlopen(req)

            #base_id = data_op.save_base(base_xml, base_name)
            #location = 'http://neo.lightbase.cc/lb/%s/view' %(base_name)
            location = 'http://neo.lightbase.cc/api'
            return HTTPFound(location=location)

    return {'project':'LBGenerator'}

@view_config(route_name='view_base', renderer='../templates/base/view.pt')
def my_view2(request):

    #/base/{base_name}/view

    base_name = request.matchdict.get("base_name")
    engine = model.Engine.engine
    session = model.Engine.session
    metadata = model.Engine.metadata
    model.define_bases_table(metadata)
    query = None
    if engine.dialect.has_table(session, 'lb_bases'):
        query = session.query(model.LB_bases).filter(model.LB_bases.nome_base == base_name).first()
    if query:
        resp = '<h2>ID da base: %s</h2>' %(query.id_base)
        resp += '<h2>Nome da base: %s</h2>' %(query.nome_base)
        resp += '<h2>XML da base:</h2>'
        resp2 = query.xml_base
    else:
        resp = '<h2>Esta base ainda não foi criada!</h2>'
        resp2 = ''

    session.close()
    return {'project':'LBGenerator', 'response':resp, 'response2':resp2}

@view_config(route_name='delete_base', renderer='../templates/base/delete.pt')
def my_view3(request):

    #/base/{base_name}/delete

    '''base_name = request.matchdict.get("base_name")
    engine, session, metadata = model.Engine().get_conn()
    bases_table, forms_table, regs_table, docs_table = model.Engine().mapper_all(base_name)
    if engine.dialect.has_table(session, 'lb_docs_%s' %(base_name)):
        metadata.drop_all(tables=[docs_table])
    if engine.dialect.has_table(session, 'lb_regs_%s' %(base_name)):
        metadata.drop_all(tables=[regs_table])
    base_id = session.query(model.LB_bases.id_base).filter(model.LB_bases.nome_base == base_name).first()
    form = session.query(model.LB_forms).filter(model.LB_forms.id_base == base_id).first()
    if form:
        session.delete(form)
    base = session.query(model.LB_bases).filter(model.LB_bases.nome_base == base_name).first()
    if base:
        session.delete(base)
        session.commit()
        session.expunge_all()
        resp = '<h2>Base %s deletada</h2>' %(base_name)
    else:
        resp = '<h2>Base não existe!</h2>'

    session.close()'''
    #return {'project':'LBGenerator', 'response':resp, 'response2':''}
    return {'project':'LBGenerator', 'response':'não implementado', 'response2':''}

@view_config(route_name='edit_base', renderer='../templates/base/edit.pt')
def my_view4(request):
    import cgi

    response = request.matchdict
    #/base/{base_name}/edit

    return {'project':'LBGenerator', 'matchdict':response}
