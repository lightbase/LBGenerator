
class PathFunctions(object):

    def __init__(self, fn, args):
        if fn is None:
            self._callfn = getattr(self, '_standard')
        else:
            self._callfn = getattr(self, '_' + fn)
        assert isinstance(args, list)
        self._args = args

    def __call__(self, value):
        return self._callfn(value)

class InsertOnPathFunctions(PathFunctions):

    def _standard(self, match):
        return (True, self._args[0])

class UpdateOnPathFunctions(PathFunctions):

    def _standard(self, match):
        return (True, self._args[0])

    def _equals(self, match):
        if match.value == self._args[0]:
            return (True, self._args[1])
        return (False, None)

    def _attr_equals(self, match):
        """
        args: ["field_in_group_to_compare", "value_to_compare", "group_to_update"]
        update the fields of group if "field_in_group_to_compare" equal "value_to_compare"
        """
        if len(self._args) is 3:
            try:
                if type(self._args[2]) is dict:
                    if self._args[1] == match.value[self._args[0]]:
                        new_value = match.value
                        for key in self._args[2]:
                            new_value[key] = self._args[2][key]
                        return (True, new_value)
                else:
                    if match.value == self._args[1]:
                        return (True, self._args[2])
            except: pass
        return (False, None)

    def _starts_with(self, match):
        if match.value.startswith(self._args[0]):
            return (True, self._args[1])
        return (False, None)

    def _replace(self, match):
        new_value =  match.value.replace(*self._args)
        return (True, new_value)

class DeleteOnPathFunctions(PathFunctions):
    # O construtor está na classe PathFunctions.

    def _standard(self, match):
        return True

    def _equals(self, match):
        if self._args[0] == match.value:
            return True
        return False

    def _attr_equals(self, match):
        """
        args: ["field_in_group", "value_to_compare", boolean]
        if boolean is true, will delete path if "field_in_group"
        exists or matches "value".
        if bolean is not true will delete path only if "field_in_group"
        value exists and matches "value".
        """

        # Essa lógica tá meio dúbia e aparentemente redundante. O
        # que ela faz?
        if len(self._args) is 3 and (self._args[2] == True or\
                self._args[2] == 'true'):
            if not self._args[0] in list(match.value.keys()):
                return True
            try:
                if match.value[self._args[0]] == self._args[1]:
                    return True
            except: pass
        else:
            try:
                if match.value[self._args[0]] == self._args[1]:
                    return True
            except: pass
        return False

def get_path_fn(path, mode, fn=None, args=[]):
    """
    Path Operation Examples:
    {
        "path": "field",
        "mode": "insert",
        "fn": null,
        "args": ["875.637.971-49"]
    }
    """

    # Defione a classe conforme a operação solicitada.
    modefns = {
        'insert': InsertOnPathFunctions,
        'update': UpdateOnPathFunctions,
        'delete': DeleteOnPathFunctions}

    try:
        # Passa os parâmetros para o contrutor de uma das classes
        # logo acima que está na classe "PathFunctions".
        # Em "fn" é definida a função a realizar a tarefa mais os
        # argumentos em "args". Se nenhuma função for definida em
        # "fn" uma função padrão é executada!
        return path.split('/'), modefns[mode](fn, args)
    except KeyError:
        raise KeyError('Mode must be %s' % str(set(modes.keys())))

# Define a operação x caminho e as funções executantes da tarefa via
# delegate.
def parse_list_pattern(base, document, pattern):

    # Define métodos conforme a operação solicitada.
    mapping = {
        'insert': base.set_path,
        'update': base.put_path,
        'delete': base.delete_path}

    # Itera no conjunto de operações definidas em pattern.
    for operation in pattern:
        path, fn = get_path_fn(**operation)
        method = mapping[operation['mode']]
        document = method(document, path, fn)

    return document

