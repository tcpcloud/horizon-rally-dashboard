
from rally import db


class Deployment(object):

    """Deployment api encapsulation
    """

    def get(self, id):

        return db.deployment_get(id)

    def list(self):

        return db.deployment_list()
