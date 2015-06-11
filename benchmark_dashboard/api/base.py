

class ApiBase(object):

    """Base api
    """

    def list(self):
        raise NotImplementedError

    def get(self, id=None):
        raise NotImplementedError

    def save(self, id=None):
        raise NotImplementedError

    def delete(self, id=None):
        raise NotImplementedError
