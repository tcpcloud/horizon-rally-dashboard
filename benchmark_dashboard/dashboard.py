
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import horizon


class Rally(horizon.Dashboard):

    name = _(getattr(settings, 'RALLY_DASHBOARD_NAME', _("Benchmark")))
    slug = "benchmark"
    #permissions = ("openstack.services.orchestration",)
    panels = ('tasks', 'deployments')
    default_panel = "tasks"
    supports_tenants = True

horizon.register(Rally)
