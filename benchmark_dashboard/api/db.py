
import json
import os

from rally import consts
import jsonschema
from django.conf import settings
from oslo_config import cfg
from oslo_db import api as db_api
from oslo_db import options as db_options
from oslo_utils import uuidutils
from rally import api, db, objects
from rally.benchmark.processing import plot
from rally.benchmark.processing.plot import _process_results
from rally.db import api as _db_api

CONF = cfg.CONF

_BACKEND_MAPPING = {"sqlalchemy": "rally.db.sqlalchemy.api"}

DB_CONNECTION = getattr(settings,
                        'RALLY_DB', "mysql://rally:password@127.0.0.1/rally")


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

    def create(self, task, deployment, **kw):

        try:
            input_task = api.Task.render_template('%s' % task, **kw)
        except Exception as e:
            raise e

        task = api.Task.create(deployment, None)
        from rally.common import fileutils
        db.task_get(task["uuid"])
        fileutils.update_globals_file("RALLY_TASK", task)

        api.Task.start(deployment, input_task, task=task,
                       abort_on_sla_failure=False)

        return self.detailed(task['uuid'])

    def delete(self, uuid, force=True):
        status = None if force else consts.TaskStatus.FINISHED
        objects.Task.delete_by_uuid(uuid, status=status)

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
