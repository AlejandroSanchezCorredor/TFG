class HTTPError(Exception):
    def __init__(self, statusCode, message=None):
        self.statusCode = statusCode
        self.message = message
