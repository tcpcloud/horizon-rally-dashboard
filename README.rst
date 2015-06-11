=======================
Horizon Rally Dashboard
=======================

Simple Rally Dashboard which provide interface for managing benchmark scenarios and their results.

Installation notes
------------------

* add `benchmark_dashboard` to INSTALLED_APPS tuple
* the default path for scenarios is `/srv/rally/scenarios`, but can be set by `RALLY_ROOT` variable

.. code-block:: python

    RALLY_ROOT = '/srv/rally/scenarios'

    RALLY_DB = "mysql://rally:password@127.0.0.1/rally"

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

Read more
---------

* http://docs.openstack.org/developer/horizon/topics/tutorial.html
