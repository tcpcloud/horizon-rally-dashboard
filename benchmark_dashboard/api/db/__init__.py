
from .base import DbBackend
from .tasks import Task
from .deployments import Deployment


class Api(DbBackend):

    """base encapsulation for us
    """

    deployments = Deployment()
    tasks = Task()

rally = Api()
