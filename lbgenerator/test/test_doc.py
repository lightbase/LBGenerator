# -*- coding: utf-8 -*-

import unittest
import requests
from mass_test import json_base
from config_tests import url_ip


class TestDoc(unittest.TestCase):

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


    def test_2_postdoc(self):
        """
        :return: Criando Doc no LBGenerator
        """
        data = '{"nome": "lightbase"}'
        payloads = {"value": data}
        response = requests.post(self.ip+'/testetest/doc', data=payloads)
        a = str(response)
        self.assertEqual(a, '<Response [200]>')

    def test_3_get(self):
        """
        :return: Get Doc
        """
        response = requests.get(self.ip+'/testetest/doc/1')
        a = str(response)
        self.assertEqual(a, '<Response [200]>')

    def test_4_put(self):
        """
        :return: Alterando a Estrutura do Doc
        """
        data = '{"nome": "lig"}'
        payloads = {"value": data}
        response = requests.put(self.ip+'/testetest/doc/1', data=payloads)
        a = str(response)
        self.assertEqual(a, '<Response [200]>')

        pass

    def test_5_delete(self):
        """
        :return: Deletando o Doc
        """
        response = requests.delete(self.ip+'/testetest/doc/1')
        a = str(response)
        self.assertEqual(a, '<Response [200]>')

    def test_6_delete(self):
        """
        :return: Deletando Base Do LBGenerator
        """
        response = requests.delete(self.ip + '/testetest')
        a = str(response)
        self.assertEqual(a, '<Response [200]>')

    def tearDown(self):
        pass
