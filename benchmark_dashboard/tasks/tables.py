
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables


class SelectTask(tables.LinkAction):
    name = "task_run"
    verbose_name = _("Task Run")
    url = "horizon:benchmark:tasks:task_select"
    classes = ("btn", "ajax-modal")

    def get_link_url(self, datum=None):
        return reverse(self.url)

    def allowed(self, request, instance):
        return True


class DetailTask(tables.LinkAction):
    name = "task_detail"
    verbose_name = _("Task Detail")
    url = "horizon:benchmark:tasks:detail"
    classes = ("btn",)

    def get_link_url(self, datum):
        return reverse(self.url, args=(datum['uuid'],))

    def allowed(self, request, instance):
        if instance.get('services', None):
            return True
        return False


class DownloadTaskReport(tables.LinkAction):
    name = "task_report"
    verbose_name = _("Download Task Report")
    url = "horizon:benchmark:tasks:report"
    classes = ("btn", "fa fa-download")

    def get_link_url(self, datum):
        return reverse(self.url, args=(datum['uuid'],))

    def allowed(self, request, instance):
        if instance.get('services', None):
            return True
        return False


class TaskTable(tables.DataTable):

    services = tables.Column("services", verbose_name=_('Services'))
    scenarios = tables.Column("scenarios", verbose_name=_('Scenarios'))
    uuid = tables.Column("uuid", verbose_name=_('UUID'), hidden=True)
    deployment = tables.Column(
        "_deployment", verbose_name=_('Deployment'), filters=(lambda d: d['name'],))

    created_at = tables.Column("created_at", verbose_name=_('Stared at'))
    updated_at = tables.Column("updated_at", verbose_name=_('Updated at'))
    duration = tables.Column("duration", verbose_name=_('Duration'))
    status = tables.Column("status", verbose_name=_('Status'))
    #results = tables.Column("results", verbose_name=_('Results'))

    def get_object_id(self, obj):
        return obj.get("uuid")

    class Meta:
        name = "tasks"
        verbose_name = _("Tasks History")
        row_actions = (DetailTask, DownloadTaskReport)
        table_actions = (SelectTask,)
