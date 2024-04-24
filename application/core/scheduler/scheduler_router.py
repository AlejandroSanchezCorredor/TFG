import re
from collections import defaultdict
from functools import wraps


class SchedulerTasker:
    handlers = defaultdict(dict)

    @staticmethod
    def task_request(event, context):
        resource = re.sub(r'^/?(.*?)/?$', r'\1', event['task'])
        return SchedulerTasker.handlers[resource](event, context)

    @staticmethod
    def task(resource):

        def inner(funct):
            @wraps(funct)
            def wrapper(*args, **kwargs):
                return funct(*args, **kwargs)
            SchedulerTasker.handlers[resource] = funct
            return wrapper

        return inner