from beaker.cache import cache_managers

__author__ = 'eduardo'


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