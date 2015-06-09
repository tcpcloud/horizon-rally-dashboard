=======================
Horizon Rally Dashboard
=======================

Simple Rally Dashboard which provide interface for managing benchmark scenarios and their results.

Installation notes
------------------

* add `benchmark_dashboard` to INSTALLED_APPS tuple
* add `benchmark_dashboard.overrides` to `customization_module` in HORIZON_CONFIG or include it from other `customization_module`
* the default path for templates is `/srv/heat/env`, but can be set by `RALLY_ROOT` variable

*Example settings for custom Heat templates*

.. code-block:: python

    RALLY_ROOT = '/srv/heat/env'

Create or clone templates at default directory /srv/heat/env or set `RALLY_ROOT` variable to point to custom location.

The name of the launched stack comes from <template_name>_<env_name>.

Template directory structure
----------------------------

This extensions requires that templates are saved in `template` directory and corresponding 
environments in `environment/<template_name>` directories.

Sample template structure with 1 template and 3 possible environments, please note the file extensions as they need to match as well.

.. code-block:: bash

    $RALLY_ROOT/template/contrail_service_chaing.hot
    $RALLY_ROOT/env/contrail_service_chaing/project01.env
    $RALLY_ROOT/env/contrail_service_chaing/project02.env
    $RALLY_ROOT/env/contrail_service_chaing/lab01.env

Read more
---------

* http://docs.openstack.org/developer/horizon/topics/tutorial.html
