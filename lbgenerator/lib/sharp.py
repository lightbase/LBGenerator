
from lbgenerator.lib import dpath
from lbgenerator.lib import utils
from copy import deepcopy

class Reference():
    def __init__(self, json):
        self.copy = deepcopy(json)
    
    def compare(self, obj):
        return self.copy == obj

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
        split = path.split(self.separator)
        structure = self.json
        fixed = [ ]
        for name in split:
            if type(structure) is dict:
                fixed.append(name)
                if not name in structure:
                    dpath.util.new(self.json, self.separator.join(fixed), [ ])
                    return [ ]
            elif type(structure) is list:
                fixed.append(name)
            structure = structure[name]
        return structure

    def set(self, path, value):
        path = self.switch_path(path)
        setted = dpath.util.set(self.json, path, value)
        if setted > 0:
            return self.json
        else:
            ref = Reference(self.json)
            dpath.util.new(self.json, path, value)
            if ref.compare(self.json):
                return False
            else:
                return self.json
        
    def new(self, path, value):
        path = self.switch_path(path)
        ref = Reference(self.json)
        value = parse_dict(value)
        
        array = self.get(path)
        if len(array) > 0:
            index = len(array)
            path = '%s%s%i' % (path, self.separator, index)
            dpath.util.new(self.json, path, value)
        else:
            index = 0
            dpath.util.new(self.json, path, [])
            path = '%s%s%i' % (path, self.separator, 0)
            dpath.util.new(self.json, path, value)

        if ref.compare(self.json):
            return False
        else:
            return index, self.json

    def delete(self, path):
        pass

def parse_dict(d):
    try:
        return utils.to_json(d)
    except:
        return d



