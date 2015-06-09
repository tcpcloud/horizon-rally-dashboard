
from django.utils.translation import ugettext_lazy as _

import horizon
from benchmark_dashboard import dashboard


class Deployments(horizon.Panel):
    name = _("Deployments")
    slug = 'deployments'


dashboard.Rally.register(Deployments)
