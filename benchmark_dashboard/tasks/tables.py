
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables

from horizon_contrib.tables import FilterAction
from benchmark_dashboard.api import rally


class SelectTask(tables.LinkAction):
    name = "task_run"
    verbose_name = _("Task Run")
    url = "horizon:benchmark:tasks:task_select"
    classes = ("btn", "ajax-modal")

    def get_link_url(self, datum=None):
        return reverse(self.url)

    def allowed(self, request, instance):
        return True


class DeleteTask(tables.DeleteAction):

    data_type_singular = 'Task'
    data_type_plural = 'Tasks'
    action_present = _("Delete")
    action_present_plural = _("Delete")

    def allowed(self, request, instance=None):
        if instance and instance['status'] == 'running':
            return False
        return True

    def action(self, request, obj_id):
        rally.tasks.delete(obj_id)


class AbortTask(tables.DeleteAction):

    name = "abort"
    data_type_singular = 'Task'
    data_type_plural = 'Tasks'
    action_present = _("Abort")
    action_past = _("Aborted")
    action_present_plural = _("Abort")

    def allowed(self, request, instance=None):
        if instance and instance['status'] == 'running':
            return True
        return False

    def action(self, request, obj_id):
        rally.tasks.abort(obj_id)


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
    tag = tables.Column("tag", verbose_name=_('Tag'))

    def get_object_id(self, obj):
        return obj.get("uuid")

    def get_display_name(self, obj):
        return obj.get("uuid")

    class Meta:
        name = "tasks"
        verbose_name = _("Tasks")
        row_actions = (DetailTask, DownloadTaskReport, DeleteTask, AbortTask,)
        table_actions = (FilterAction, SelectTask, AbortTask, DeleteTask,)
