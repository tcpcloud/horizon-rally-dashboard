=======================
Horizon Rally Dashboard
=======================

Simple Rally Dashboard which provide interface for managing benchmark scenarios and their results.

For more infromation read my blog post `Benchmarking OpenStack for Humans <http://majklk.cz/blog/2015/06/11/benchmarking-openstack-humans/>`_

Installation notes
------------------

* add `benchmark_dashboard` to INSTALLED_APPS tuple
* the default path for scenarios is `/srv/rally/scenarios`, but can be set by `RALLY_ROOT` variable

.. code-block:: python

    RALLY_ROOT = '/srv/rally/scenarios'

    RALLY_DB = "mysql://rally:password@127.0.0.1/rally"

    RALLY_PLUGINS = [
        'rally.plugins.openstack',
        'rally.plugins.common'
    ]

    # or load all

    RALLY_PLUGINS = [
        'rally.plugins',
    ]

Create or clone scenarios at default directory /srv/rally/scenarios or set `RALLY_ROOT` variable to point to custom location.

Serving scenarios
-----------------

.. code-block:: bash

    root@web01:/srv/rally# ls -la /srv/rally/scenarios/tasks/scenarios/nova/
        boot-and-delete-multiple.yaml
        boot-and-delete-server-with-keypairs.yaml
        boot-and-delete-server-with-secgroups.yaml
        boot-and-delete.yaml
        boot-from-volume-and-delete.yaml
        boot-snapshot-boot-delete.yaml
        create-and-delete-secgroups.yaml

Long running tasks
------------------

We create new Thread for every task, which is basically wrong and may cause overload your Horizon, but you can simple overwrite async task behaviour.

.. code-block:: python

    def run_async(method):

        # call Celery or whatever

        Thread(target=method, args=[]).start()

Set it to ``benchmark_dashboard.utils.async``

Read more
---------

* http://docs.openstack.org/developer/horizon/topics/tutorial.html
