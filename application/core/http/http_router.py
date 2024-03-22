import re
from collections import defaultdict
from functools import wraps
from .http_error import HTTPError


class HTTPRouter:
    ALL_WILDCARD = '*'
    handlers = defaultdict(dict)

    @staticmethod
    def route_request(event, context): # Buscamos si existe el recurso
        resource = re.sub(r'^/?(.*?)/?$', r'\1', event['resource'])
        if resource in HTTPRouter.handlers:
            http_method = event['httpMethod'].lower()
            if http_method in HTTPRouter.handlers[resource]:
                return HTTPRouter.handlers[resource][http_method](event, context)
            elif HTTPRouter.ALL_WILDCARD in HTTPRouter.handlers[resource]:
                return HTTPRouter.handlers[resource][HTTPRouter.ALL_WILDCARD](event, context)
            raise HTTPError(405)
        raise HTTPError(404)

    @staticmethod
    def route(resource, *http_verbs): 
        def inner(funct):
            @wraps(funct)
            def wrapper(*args, **kwargs):
                return funct(*args, **kwargs)

            for http_verb in http_verbs or [HTTPRouter.ALL_WILDCARD]:
                HTTPRouter.handlers[resource][http_verb.lower()] = funct
            return wrapper

        return inner