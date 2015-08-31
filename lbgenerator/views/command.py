import os
import socket
import fcntl
import struct
from ..model import BASES
from .. import config
from pyramid.response import Response
from liblightbase.lbutils import object2json
from sqlalchemy import create_engine

class CommandCustomView():

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def execute(self):

        command = self.request.matchdict['command']
        return getattr(self, command)()

    def reset(self):
            BASES.bases = dict()
            try:
                os.system('/etc/init.d/apache2 restart')
                return Response('OK')
            except:
                os.system('/etc/init.d/httpd restart')
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

    def db_url(self):
        return Response(config.DB_URL)

    def rest_url(self):
        return Response(get_ip_address(b'eth0'))

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


