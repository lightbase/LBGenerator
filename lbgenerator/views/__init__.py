from pyramid.view import view_config
from sqlalchemy import create_engine

@view_config(route_name='home', renderer='../templates/mytemplate.pt')
def my_view(request):
    #engine = create_engine('postgresql://postgres@10.0.0.154/gerador_bases')
    #connection = engine.connect()
    #connection.execute('commit;')
    #result = connection.execute("SELECT nome_base FROM lb_bases ;")
    #connection.close()
    #links = list()
    #for row in result:
    #    for base in row:
    #        links.append('<a href="http://neo.lightbase.cc/lb/%s/view">%s</a>' %(base, base))
    return {'project':'LBGenerator','bases':[]}

