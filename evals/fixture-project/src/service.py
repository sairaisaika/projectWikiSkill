"""Offline fixture service. It only calls the injected dependency."""


def get_articles(source, query):
    rows = source.list_articles(query)
    if rows is None:
        return {'ok': False, 'error': 'unavailable'}
    return {'ok': True, 'data': rows}
