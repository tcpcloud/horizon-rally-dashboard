
from django.utils.translation import ugettext_lazy as _

import horizon
from benchmark_dashboard import dashboard


class Tasks(horizon.Panel):
    name = _("Tasks")
    slug = 'tasks'


dashboard.Rally.register(Tasks)
