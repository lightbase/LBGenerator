import os
import fcntl
import socket
import struct

from .. import config
from sqlalchemy import create_engine
from pyramid.response import Response
from liblightbase.lbutils import object2json

from ..model import BASES
from ..model.context.file import FileContextFactory


class CommandCustomView():

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def execute(self):
        command = self.request.matchdict['command']

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if self.context.session.is_active:
                self.context.session.close()
        except:
            pass

        return getattr(self, command)()

    def reset(self):
            BASES.bases = dict()

            # NOTE: Comando que mata todas as conexões com o banco de dados!
            # By John Doe
            config.ENGINE.dispose()

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
        0x8915, # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

