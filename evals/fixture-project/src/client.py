"""Legacy fixture client: failures become None, success keeps the list."""


def read_articles(service, source, query):
    result = service(source, query)
    return result['data'] if result['ok'] else None
