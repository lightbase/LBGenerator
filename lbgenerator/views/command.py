from ..model import BASES
from pyramid.response import Response

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
        v1 = pkg_resources.get_distribution('lbgenerator').version
        v2 = pkg_resources.get_distribution('liblightbase').version
        return Response('%s + %s' % (v1, v2))
