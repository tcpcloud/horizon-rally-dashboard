
import json
import os

import jsonschema
import yaml
from benchmark_dashboard.utils.async import run_async
from django.conf import settings
from oslo_config import cfg
from oslo_db import api as db_api
from oslo_db import options as db_options
from oslo_utils import uuidutils
from rally import api, consts, db, exceptions, objects
from rally.benchmark import engine
from rally.benchmark.processing import plot
from rally.benchmark.processing.plot import _process_results
from rally.common import log as logging
from rally.common import utils
from rally.db import api as _db_api
from .loader import load_all_stuff

LOG = logging.getLogger(__name__)

CONF = cfg.CONF

_BACKEND_MAPPING = {"sqlalchemy": "rally.db.sqlalchemy.api"}

DB_CONNECTION = getattr(settings,
                        'RALLY_DB', "mysql://rally:password@127.0.0.1/rally")

RALLY_BASIC_PLUGINS = [
    'rally.plugins.openstack',
    'rally.plugins.common'
]

RALLY_PLUGINS = getattr(settings, 'RALLY_PLUGINS', RALLY_BASIC_PLUGINS)

# this stuff may take some time and may raise exception
for plugin in RALLY_PLUGINS:
    try:
        load_all_stuff(plugin)
    except Exception as e:
        LOG.error(str(e))


def _patch_db_config():
    """propagate db config down to rally
    """

    db_options.set_defaults(CONF, connection=DB_CONNECTION,
                            sqlite_db="rally.sqlite")

    IMPL = db_api.DBAPI.from_config(CONF, backend_mapping=_BACKEND_MAPPING)

    _db_api.IMPL = IMPL


class DbBackend(object):

    """Base api
    """

    def __init__(self, *args, **kwargs):
        _patch_db_config()
        super(DbBackend, self).__init__(*args, **kwargs)



class Task(DbBackend):

    """Task api encapsulation
    """

    def list(self, **kwargs):

        task_list = db.task_list()

        deployments = Deployment().list()

        for x in task_list:
            x["duration"] = x["updated_at"] - x["created_at"]
            # ugly mapping
            for d in deployments:
                if x['deployment_uuid'] == d['uuid']:
                    x._deployment = d

            try:
                source, results = self.report(x['uuid'])
                scenarios = []
                services = []
                for sc in json.loads(source).keys():
                    services.append(sc.split('.')[0])
                    scenarios.append(sc.split('.')[1])
                x['services'] = ', '.join(services)
                x['scenarios'] = ', '.join(scenarios)
                x['_results'] = results
            except Exception as e:
                raise e

        return task_list

    def report(self, task, **kw):
        tasks_results = map(
            lambda x: {"key": x["key"],
                       "sla": x["data"]["sla"],
                       "result": x["data"]["raw"],
                       "load_duration": x["data"]["load_duration"],
                       "full_duration": x["data"]["full_duration"]},
            objects.Task.get(task).get_results())
        return _process_results(tasks_results)

    def plot(self, task):
        return plot.plot(self.results(task))

    def results(self, task, **kw):
        tasks_results = map(
            lambda x: {"key": x["key"],
                       "sla": x["data"]["sla"],
                       "result": x["data"]["raw"],
                       "load_duration": x["data"]["load_duration"],
                       "full_duration": x["data"]["full_duration"]},
            objects.Task.get(task).get_results())
        return tasks_results

    def _get_descriptions(self, base_cls, subclass_filter=None):
        descriptions = []
        subclasses = utils.itersubclasses(base_cls)
        if subclass_filter:
            subclasses = filter(subclass_filter, subclasses)
        for entity in subclasses:
            name = entity.get_name()
            doc = utils.parse_docstring(entity.__doc__)
            description = doc["short_description"] or ""
            descriptions.append((name, description))
        descriptions.sort(key=lambda d: d[0])
        return descriptions

    def create(self, task, deployment, tag=None, **kw):

        try:
            input_task = api.Task.render_template('%s' % task, **kw)
        except Exception as e:
            raise e

        # we don't know what is there
        try:
            input_task = json.loads(input_task)
        except Exception as e:
            input_task = yaml.load(input_task)

        task = api.Task.create(deployment, tag)
        db.task_get(task["uuid"])

        self.start(deployment, input_task, task=task,
                   abort_on_sla_failure=False)

        return task

    @classmethod
    def start(cls, deployment, config, task=None, abort_on_sla_failure=False):
        """Start a task.
        Task is a list of benchmarks that will be called one by one, results of
        execution will be stored in DB.
        :param deployment: UUID or name of the deployment
        :param config: a dict with a task configuration
        :param task: Task object. If None, it will be created
        :param abort_on_sla_failure: if True, the execution of a benchmark
                                     scenario will stop when any SLA check
                                     for it fails
        """
        deployment = objects.Deployment.get(deployment)
        task = task or objects.Task(deployment_uuid=deployment["uuid"])
        LOG.info("Benchmark Task %s on Deployment %s" % (task["uuid"],
                                                         deployment["uuid"]))
        benchmark_engine = engine.BenchmarkEngine(
            config, task, admin=deployment["admin"], users=deployment["users"],
            abort_on_sla_failure=abort_on_sla_failure)

        try:
            benchmark_engine.validate()

            run_async(benchmark_engine.run)

        except exceptions.InvalidTaskException as e:
            raise e
        except Exception as e:
            deployment.update_status(consts.DeployStatus.DEPLOY_INCONSISTENT)
            raise e

    def delete(self, uuid, force=True):
        status = None if force else consts.TaskStatus.FINISHED
        objects.Task.delete_by_uuid(uuid, status=status)

    def abort(self, uuid):
        """not implemented yet
        """
        objects.Task.abort(uuid)

    def detailed(self, uuid):
        return db.task_get_detailed(uuid)


class Deployment(object):

    """Deployment api encapsulation
    """

    def get(self, id):

        return db.deployment_get(id)

    def list(self):

        return db.deployment_list()


class Api(DbBackend):

    """base encapsulation for us
    """

    deployments = Deployment()
    tasks = Task()
