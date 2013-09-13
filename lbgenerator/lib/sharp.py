
from lbgenerator.lib import dpath

def switch_path(path, separator='/'):
    parsed_path = path.replace('.', separator).replace(']', '').replace('[', separator)
    if parsed_path[0] == separator: parsed_path = parsed_path[1:]
    return parsed_path

class SharpJSON(object):
    
    def __init__(self, json):
        self.json = json

    def set(self, path, value):
        path = switch_path(path)
        setted = dpath.util.set(self.json, path, value)
        if setted > 0:
            return self.json
        else:
            return False
        
    def new(self, path, value):
        path = switch_path(path)
        setted = dpath.util.new(self.json, path, value)
        if setted > 0:
            return self.json
        else:
            return False
