
from . import CustomContextFactory

class ESContextFactory(CustomContextFactory):

    def __init__(self, request):
        self.request = request
