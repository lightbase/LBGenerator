# -*- coding: utf-8 -*-

import unittest
import requests
from .mass_test import json_base
from .config_test import url_ip


class TestDoc(unittest.TestCase):

    def setUp(self):
        self.base = json_base
        self.ip = url_up

    def test_post_file(self):
        """
        :return: Inserindo File no LBGenerator !!! Não implementado !!!
        """
        pass

    def test_get_File(self):
        """
        :return: Get File !!! Não implementado !!!
        """
        pass

    def test_put_file(self):
        """
        :return: Alterando a Estrutura do File !!! Não implementado !!!
        """
        pass

    def test_delete_file(self):
        """
        :return: Deletando o File !!! Não implementado !!!
        """
        pass


    def tearDown(self):
        pass
