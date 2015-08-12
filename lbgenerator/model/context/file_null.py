# -*- coding: utf-8 -*-

from . import CustomContextFactory
from .. import file_entity


class FileNullContextFactory(CustomContextFactory):

    def __init__(self):
        super(FileNullContextFactory, self).__init__(request)
        self.entity = file_entity(self.base_name)

    def get_null_file(self):
        pass

