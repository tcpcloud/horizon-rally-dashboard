
from django.conf import settings
from oslo_config import cfg
from oslo_db import api as db_api
from oslo_db import options as db_options
from rally.common import log as logging
from rally.db import api as _db_api
from benchmark_dashboard.api.loader import load_all_stuff

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
