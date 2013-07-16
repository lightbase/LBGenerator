import unittest
import os.path
import sys

from pyramid import testing
import liblightbase
import liblightbase.lbbase
from lbgenerator import lib
from lbgenerator.lib import elastics
from liblightbase.lbbase import Base
from liblightbase.lbbase.xml import base_to_xml
from lbgenerator.views import base



class ViewTests(unittest.TestCase):

    def setUp(self):

        self.ES_test = elastics.ESconnecor()
        self.config = testing.setUp()

    def test_create_index(self):

        self.ES_test.create_index()

    def test_delete_index(self):

        self.ES_test.delete_index()

    def test_refresh_index(self):

        self.ES_test.refresh_index()

    def test_index_document(self):

        self.ES_test.index_document()

    def test_indices(self):

        self.ES_test.indices()

    def test_check_index(self):

        self.ES_test.check_index()

    def test_create_types(self):

        self.ES_test.create_types()

    def test_query(self):

        self.ES_test.query()

    def test_to_json(self):

        self.ES_test.to_json()

    def test_my_view(self):

        '''from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'LBGenerator')'''

    def tearDown(self):

        testing.tearDown()
