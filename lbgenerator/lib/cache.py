# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import re
import logging
from beaker.cache import cache_managers
from copy import deepcopy

log = logging.getLogger()


def clear_cache(name=None):
    """
    Clear all cache from beaker
    :param name: Cache name to be clared
    :return: True
    """
    for _cache in cache_managers.values():
        if name is not None and _cache == name:
            # Clear only this cache
            _cache.clear()
            break

        _cache.clear()

    return True

def clear_collection_cache(base):
    """
    Clear all cache for the base

    :param base: Base name for cache clean
    :return: True or False
    """
    result = False

    # I have to copy the object to avoid RunTime Error
    managers = deepcopy(cache_managers)
    for manager_key in managers.keys():
        _cache = managers[manager_key]
        key = "/cached/" + base + "/doc"
        key_list = _cache.namespace.keys()
        for cache_key in key_list:
            cache_key_str = cache_key.decode()

            # Search all keys for this base and remove it
            r = re.search(key, cache_key_str)
            if r is not None:
                log.debug("Clearing cache for key %s", cache_key)
                obj = cache_managers[manager_key]
                obj.remove_value(cache_key)

        result = True

    return result


def clear_document_cache(base, id_doc):
    """
    Clear cache for this document

    :param base: Base name
    :param id_doc: DocumentID
    :return: True or False
    """
    result = False

    # I have to copy the object to avoid RunTime Error
    managers = deepcopy(cache_managers)
    for manager_key in managers.keys():
        _cache = managers[manager_key]
        # FIXME: Get close_sess from the class. It defaults to True and there's no other possibility
        close_sess = "True"
        key = "/cached/" + base + "/doc/" + str(id_doc) + " " + str(id_doc) + " " + close_sess
        key = key.encode()
        try:
            value = _cache.get(key)
            log.debug("Clearing cache for key %s", key)
            obj = cache_managers[manager_key]
            obj.remove_value(key)
        except KeyError as e:
            log.debug("Key %s not found", e)

        result = True

    return result