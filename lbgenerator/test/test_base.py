# -*- coding: utf-8 -*-

import unittest
import requests
import json
from mass_test import json_base
from config_tests import url_ip


class TestBase(unittest.TestCase):

    def setUp(self):
        self.base = json_base
        self.ip = url_ip

    def test_1_post(self):
        """
        :return: Criando Base no LBGenerator
        """
        data = {'json_base': self.base}
        response = requests.post(self.ip, data=data)
        a = str(response)
        self.assertEqual(a, '<Response [200]>')

    def test_2_get(self):
        """
        :return: Get Base
        """
        response = requests.get(self.ip + '/testetest')
        a = str(response)
        self.assertEqual(a, '<Response [200]>')


    def test_3_put(self):
        """
        :return: Alterando a Estrutura da Base. !!! ainda não implementado !!!
        """
        pass

    def test_4_delete(self):
        """
        :return: Deletando a Base
        """
        response = requests.delete(self.ip + '/testetest')
        a = str(response)
        self.assertEqual(a, '<Response [200]>')

    def tearDown(self):
        pass
