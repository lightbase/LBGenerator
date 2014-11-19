from ..model import BASES
from pyramid.response import Response
from liblightbase.lbutils import object2json

class CommandCustomView():

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def execute(self):

        command = self.request.matchdict['command']
        try:
            return getattr(self, command)()
        except:
            raise Exception('Command Not Found')

    def reset(self):
        BASES.bases = dict()
        return Response('OK')

    def base_mem(self):
        return Response(str(list(BASES.bases.keys())))

    def version(self):
        import pkg_resources
        lbg = pkg_resources.get_distribution('lbgenerator')
        versions = { }
        for requirement in lbg.requires():
            try:
                req_name = requirement.project_name
                req_version = pkg_resources.get_distribution(req_name).version
                versions[req_name] = req_version
            except: pass
        versions['lbgenerator'] = lbg.version
        return Response(object2json(versions), content_type='application/json')
