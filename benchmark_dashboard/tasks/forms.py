import json
import logging
import yaml
import six
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa
from django.conf import settings
from horizon import exceptions
from horizon import forms
from horizon import messages
from oslo.utils import strutils
from openstack_dashboard import api

from benchmark_dashboard.utils import get_tasks, get_contexts, \
    get_task_filename, get_environment_data, CustomEncoder, get_task_data, get_services, get_context_data

LOG = logging.getLogger(__name__)

HEAT_LOCAL = getattr(settings, "HEAT_LOCAL", True)
# allow url, raw and file inputs
# prevent user fail
HEAT_LOCAL_ONLY = getattr(settings, "HEAT_LOCAL_ONLY", True)
HIDE_SOURCE = getattr(settings, "HIDE_SOURCE", True)

from benchmark_dashboard.api import rally


def create_upload_form_attributes(prefix, input_type, name):
    """Creates attribute dicts for the switchable upload form

    :type prefix: str
    :param prefix: prefix (environment, template) of field
    :type input_type: str
    :param input_type: field type (file, raw, url)
    :type name: str
    :param name: translated text label to display to user
    :rtype: dict
    :return: an attribute set to pass to form build
    """
    attributes = {'class': 'switched', 'data-switch-on': prefix + 'source'}
    attributes['data-' + prefix + 'source-' + input_type] = name
    return attributes


class TaskSelectForm(forms.SelfHandlingForm):

    class Meta:
        name = _('Launch Template')
        help_text = _('From here you can select and launch a template.')

    template_data = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False)

    environment_data = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False)

    stack_name = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False)

    tag = forms.CharField(
        required=False)

    deployment = forms.ChoiceField(label=_('Deployment'),
                                   choices=[
        (d['uuid'], d['name']) for d in rally.deployments.list()],
        widget=forms.Select(),
        required=True)

    context = forms.ChoiceField(label=_('Context'),
                                choices=get_contexts(),
                                widget=forms.Select(),
                                required=True)

    attributes = {'class': 'switchable', 'data-slug': 'localsource'}
    choices = get_services()
    service = forms.ChoiceField(label=_('Service'),
                                choices=choices,
                                widget=forms.Select(attrs=attributes),
                                required=True)

    def __init__(self, request, *args, **kwargs):
        self.next_view = kwargs.pop('next_view')
        super(TaskSelectForm, self).__init__(request, *args, **kwargs)

        for service in get_services():
            attributes = create_upload_form_attributes(
                'local',
                '%s' % service[0],
                _('Tasks'))
            field = forms.ChoiceField(label=_('Tasks'),
                                      choices=get_tasks(service[0]),
                                      widget=forms.Select(
                                          attrs=attributes),
                                      required=False)
            self.fields["task____%s" % service[0]] = field

        self.fields['edit'] = forms.BooleanField(
            label=_('Edit ?'),
            help_text=_('Edit before run task.'),
            required=False)

    def clean(self):
        cleaned = super(TaskSelectForm, self).clean()

        service_name = cleaned["service"]
        task_name = cleaned["task____%s" % service_name]
        cleaned["task_data"] = get_task_data("%s/%s" % (service_name, task_name))

        return cleaned

    def handle(self, request, data):

        task_raw = data.get('task_data')

        fields = {
            'deployment': data.get('deployment'),
            'task_data': task_raw,
            'tag': data.get('tag', None),
            'context_data': get_context_data(data.get('context')),
        }

        # redirect to edit
        if data.pop("edit"):
            kwargs = fields
            # NOTE (gabriel): This is a bit of a hack, essentially rewriting this
            # request so that we can chain it as an input to the next view...
            # but hey, it totally works.
            request.method = 'GET'

            return self.next_view.as_view()(request, **kwargs)

        else:
            try:
                task = rally.tasks.create(
                    task_raw, data.get('deployment'), data.get("tag", None), **fields['context_data'])
                messages.success(
                    request, 'Task {} was successfully started.'.format(task['uuid']))
            except Exception as e:
                raise e

        return True


class TaskStartForm(forms.SelfHandlingForm):

    tag = forms.CharField(
        required=False)

    deployment = forms.ChoiceField(label=_('Deployment'),
                                   choices=[
        (d['uuid'], d['name']) for d in rally.deployments.list()],
        widget=forms.Select(),
        required=True)

    context_data = forms.CharField(
        widget=forms.widgets.Textarea,
        required=False)

    task_data = forms.CharField(
        widget=forms.widgets.Textarea,
        required=False)

    def handle(self, request, data):

        try:
            task = rally.tasks.create(
                data.get('task_data'),
                data.get('deployment'),
                data.get("tag", None),
                **yaml.load(data.get('context_data')))
            messages.success(
                request,
                'Task {} was successfully started.'.format(task['uuid']))
        except Exception as e:
            raise e

        return True
