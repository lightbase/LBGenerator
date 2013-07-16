import unittest

from pyramid import testing
import liblightbase
import liblightbase.lbbase
import lbgenerator
import lbgenerator.views
from lbgenerator import lib
from lbgenerator.lib import generator
from liblightbase.lbbase import Base
from liblightbase.lbbase.campos import CampoObjeto,Campo,Indice,Tipo
from liblightbase.lbbase.xml import base_to_xml
from lbgenerator.views import base
import os.path
import sys
import sqlalchemy
from sqlalchemy import create_engine

import webob.multidict
from webob.multidict import MultiDict


class ViewTests(unittest.TestCase):

    def setUp(self):
        dict_test = dict({('base.nome', 'rvev'), ('base.descricao', 's'), ('base.senha', 'rvrev'), ('base.objeto.campo.0.nome', 'e4f'), ('base.objeto.campo.0.descricao', 'f4f'), ('base.objeto.campo.0.tipo', 'Documento'), ('base.objeto.campo.0.indice', 'Ordenado'), ('base.objeto.campo.0.objeto.campo.1.nome', '34fg43fg'), ('base.objeto.campo.0.objeto.campo.1.descricao', 'fg'), ('base.objeto.campo.0.objeto.campo.1.tipo', 'Decimal'), ('base.objeto.campo.0.objeto.campo.1.indice', 'Unico'), ('base.objeto.campo.0.objeto.campo.1.indice', 'Fuzzy')})

        self.obj_test = b'<?xml version="1.0" encoding="utf-8"?> <base> <senha> <![CDATA[rvrev]]>    </senha> <descricao> <![CDATA[s]]>  </descricao> <nome> <![CDATA[rvev]]>    </nome> <objeto> <campo> <tipo>Documento</tipo> <indexacao> <indice>Ordenado</indice> </indexacao> <descricao> <![CDATA[f4f]]>   </descricao> <nome> <![CDATA[e4f]]>     </nome> <objeto> <campo> <tipo>Decimal</tipo> <descricao> <![CDATA[fg]]>    </descricao> <nome> <![CDATA[34fg43fg]]>    </nome> <indexacao> <indice>Unico</indice> <indice>Fuzzy</indice> </indexacao> </campo> </objeto> </campo> </objeto> </base>'

        self.field_test = {'indice': ['Ordenado'], 'objeto.campo.1.tipo': 'Decimal', 'tipo': 'Documento', 'objeto.campo.1.nome': '34fg43fg', 'nome': 'e4f', 'objeto.campo.1.indice': ['Unico', 'Fuzzy'], 'objeto.campo.1.descricao': 'fg', 'descricao': 'f4f'}

        self.multidict_test = MultiDict(dict_test)
        self.gen_test = generator.LBGenerator()
        self.config = testing.setUp()

    def test_create_base(self):

        self.gen_test.create_base(self.multidict_test)

    def test_validate_form(self):

        self.gen_test.validate_form(self.multidict_test)

    def test_xml_to_json(self):

        self.gen_test.xml_to_json(self.obj_test)

    def test_save_base_row(self):

        self.gen_test.save_base_row(self.obj_test,table='gerador_bases_teste')

    def test_parse_campo(self):

        self.gen_test.parse_campo(self.field_test)

    def test_parse_request(self):

        self.gen_test.parse_request(self.multidict_test,'gerador_bases_teste')

    def test_my_view(self):

        '''from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'LBGenerator')'''

    def tearDown(self):

        engine_test = create_engine('postgresql://postgres@10.0.0.154/gerador_bases')
        connection_test = engine_test.connect()
        connection_test.execute('commit')
        connection_test.execute('TRUNCATE TABLE gerador_bases_teste')
        testing.tearDown()
