
from lbgenerator.lib import dpath

class SharpJSON(object):
    
    def __init__(self, json):
        self.json = json
        self.separator = '/'

    def switch_path(self, path):
        parsed_path = path.replace('.', self.separator).replace(']', '').replace('[', self.separator)
        if parsed_path[0] == self.separator: parsed_path = parsed_path[1:]
        return parsed_path

    def get(self, path):
        path = self.switch_path(path)
        return []

    def set(self, path, value):
        path = self.switch_path(path)
        setted = dpath.util.set(self.json, path, value)
        if setted > 0:
            return self.json
        else:
            unmodified = dict(self.json)
            dpath.util.new(self.json, path, value)
            if self.json == unmodified:
                return False
            else:
                return self.json
        
    def new(self, path, value):
        path = self.switch_path(path)
        unmodified = dict(self.json)

        array = self.get(path)
        if array:
            index = len(array) + 1
            path = '%s%s%i' % (path, self.separator, index)
            dpath.util.new(self.json, path, value)
        else:
            dpath.util.new(self.json, path, [])
            path = '%s%s%i' % (path, self.separator, 0)
            dpath.util.new(self.json, path, value)

        if self.json == unmodified:
            return False
        else:
            return self.json




