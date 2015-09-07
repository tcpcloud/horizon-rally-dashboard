
=======================
Horizon Rally Dashboard
=======================

Horizon Rally Dashboard for quick and easy running benchmark scenarios and viewing their results.

Installation
============

#. Add `benchmark_dashboard` to INSTALLED_APPS tuple.
#. The default path for scenario definitions is at ``/srv/rally/scenarios``, but it altered with ``RALLY_ROOT`` variable in ``local_settings.py`` of your Horizon installation.

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

Create or clone your scenario definitions to default location ``/srv/rally/scenarios`` or set ``RALLY_ROOT`` variable to your location.

Usage
=====

Serving scenarios
-----------------

.. code-block:: bash

    ls -la /srv/rally/scenarios/tasks/scenarios/nova/

    boot-and-delete-multiple.yaml
    boot-and-delete-server-with-keypairs.yaml
    boot-and-delete-server-with-secgroups.yaml
    boot-and-delete.yaml
    boot-from-volume-and-delete.yaml
    boot-snapshot-boot-delete.yaml
    create-and-delete-secgroups.yaml

Long running tasks
------------------

Now a new Thread is created for every task, which may cause Horizon overload, but async task behaviour can be overwritten:

.. code-block:: python

    def run_async(method):

        # call Celery or whatever

        Thread(target=method, args=[]).start()

Set the method to ``benchmark_dashboard.utils.async`` to enable acynchronous task.

Read more
=========

* https://rally.readthedocs.org/en/latest/
* http://docs.openstack.org/developer/horizon/topics/tutorial.html
