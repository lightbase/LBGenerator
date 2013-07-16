# -*- coding: UTF-8 -*-
import os.path
import sys
import xmltodict
import json
import xml.etree.ElementTree as ET
#import pyes
#from pyes import *


class ESConnector():

    def __init__(self):
        """
        constructor parameters
        """
        # FIXME: Get this from configuration or somewhere else
        self.default_index = 'some_index'
        self.conn = ES('10.0.0.154:9200')
        self.manager = managers.Indices(self.conn)

    def create_index(self,index=None):
        """
        Create supplied indice
        """
        # TODO: Find some way user can supply these options
        settings = {
          "settings": {
           "number_of_shards":"5",
           "number_of_replicas":"1",
            "analysis.analyzer.default.filter.0":"lowercase",
            "analysis.analyzer.default.filter.1":"asciifolding",
            "analysis.analyzer.default.tokenizer":"standard",
            "analysis.analyzer.default.type":"custom",
            "analysis.filter.pt_stemmer.type":"stemmer",
            "analysis.filter.pt_stemmer.name":"portuguese"
           }
        }
        if index:
            response = self.manager.create_index(index,settings=settings)
        else:
            response = self.manager.create_index(self.default_index,settings=settings)
        return response

    def delete_index(self,index=None):
        """
        Remove supplied index
        """
        if self.exists_index(index):
            response = self.manager.delete_index(index)
        elif self.exists_index(self.default_index):
            # If not supplied, remove default index
            response = self.manager.delete_index(self.default_index)
        else:
            raise Exception('You have to create an index first. Execute create_index()')
        return response

    def index(self,doc,doc_type,id,index=None):
        """
        Index a document on ES
        """
        if index:
            self.conn.index(doc,index,doc_type,id=id)
        else:
            # If index is not supplied, index the doc to default index
            self.conn.index(doc,self.default_index,doc_type,id=id)
        return True

    def get_indices(self,include_aliases=False):
        """
        Get ES indices
        """
        return self.manager.get_indices(include_aliases=include_aliases)

    def update_settings(self,index,newvalues):
        """
        Update index settings.
        """
        return self.manager.update_settings(index,newvalues)

    def get_settings(self,index=None):
        """
        Get ES index settings
        """
        if index:
            return self.manager.get_settings(index=index)
        elif self.exists_index(self.default_index):
            return self.manager.get_settings(index=self.default_index)
        else:
            raise Exception('You have to create an index first. Execute create_index()')

    def put_mapping(self,doc_type=None,mapping=None,indices=None):
        """
        Register specific mapping definition for a specific type against one or more indices
        """
        return self.manager.put_mapping(doc_type=doc_type,mapping=mapping,indices=indices)

    def delete_mapping(self,index,doc_type):
        """
        Delete ES index mapping
        """
        return self.manager.delete_mapping(index, doc_type)

    def get_mapping(self,doc_type=None,indices=None):
        """
        Get ES index settings
        """
        return self.manager.get_mapping(doc_type=doc_type,indices=indices)

    def exists_index(self, index):
        """
        Check if supplied index exists
        @param index: indice to be checked
        """

        return self.manager.exists_index(index)

    def search(self,field,value):
        """
        Execute a search against one or more indices to get the resultset.

        `query` must be a Search object, a Query object, or a custom
        dictionary of search parameters using the query DSL to be passed
        directly.

        See: http://pyes.readthedocs.org/en/latest/guide/reference/query-dsl/index.html

        """
        query = TermQuery(field,value)
        result = self.conn.search(query)
        return result

    def xml_to_json(self,obj):
         """
         Receives a xml and return a valid json
         """
         xml_dict = xmltodict.parse(obj)
         new_obj = json.dumps(xml_dict)
         return new_obj








