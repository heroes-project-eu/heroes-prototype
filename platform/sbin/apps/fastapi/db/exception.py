class ObjectException(Exception):
    pass


class ObjectNotFoundError(ObjectException):
    def __init__(self, object=None):
        self.status_code = 404
        self.detail = f"{object} Not Found"
