cache_master = dict()


'''
TODO: Criar um esquema p/ dimensionar o tamanho da lista e o tempo em 
memória! By Questor
'''
class CacheMaster():
    """ Essa classe se propõe controlar o uso de cache de dados na 
    aplicação.
    """

    def get_cache_master(self):
        """ Gerencia o uso da variável global "cache_master" que pode 
        guardar dados de cache p/ várias rotas!
        """
        global cache_master
        if cache_master.get(self.base_name, None) is None:
            cache_master[self.base_name] = dict()
        return cache_master[self.base_name]

    def get_item(self, item_key):
        """ Obtêm o item do cache p/ a rota em questão!
        """
        return self.get_cache_master().get(item_key, None)

    def set_item(self, item_key, item_value):
        """ Seta o item do cache p/ a rota em questão!
        """
        self.get_cache_master()[item_key] = item_value

    def remove_item(self, item_key):
        """ Remove o item do cache p/ a rota em questão!
        """
        try:
            delattr(self.get_cache_master(), item_key)
        except Exception:
            pass

    def refresh_item(self, item_key, item_value, new_item_key=None):
        """ Atualiza o item do cache p/ a rota em questão!
        """
        if new_item_key is None:
            self.get_cache_master()[item_key] = item_value
        else:
            self.remove_item(item_key)
            self.get_cache_master()[new_item_key] = item_value
