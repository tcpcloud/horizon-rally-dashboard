
from django.utils.translation import ugettext_lazy as _
from horizon import tables


class DeploymentTable(tables.DataTable):

    uuid = tables.Column("uuid", verbose_name=_('UUID'))
    name = tables.Column("name", verbose_name=_('Name'))
    created_at = tables.Column("created_at", verbose_name=_('Created At'))
    status = tables.Column("status", verbose_name=_('Status'))
    active = tables.Column("active", verbose_name=_('Active'))

    def get_object_id(self, obj):
        return obj.get("uuid")

    class Meta:
        name = "deployments"
        verbose_name = _("Deployments")
