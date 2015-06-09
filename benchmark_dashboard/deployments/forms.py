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

from heat_server_templates.utils import get_templates, get_environments, \
    get_template_data, get_environment_data, CustomEncoder

LOG = logging.getLogger(__name__)

HEAT_LOCAL = getattr(settings, "HEAT_LOCAL", True)
# allow url, raw and file inputs
# prevent user fail
HEAT_LOCAL_ONLY = getattr(settings, "HEAT_LOCAL_ONLY", True)
HIDE_SOURCE = getattr(settings, "HIDE_SOURCE", True)

from heat_server_templates.utils.widgets import JSONWidget


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


class LocalTemplateStackForm(forms.SelfHandlingForm):

    class Meta:
        name = _('Launch Template')
        help_text = _('From here you can select and launch a template.')

    template_data = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False)

    environment_data = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False)

    parameters = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False)

    stack_name = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False)

    timeout_mins = forms.IntegerField(
        initial=60,
        label=_('Creation Timeout (minutes)'),
        help_text=_('Stack creation timeout in minutes.'),
        required=True)

    enable_rollback = forms.BooleanField(
        label=_('Rollback On Failure'),
        help_text=_('Enable rollback on create/update failure.'),
        required=False)

    edit = forms.BooleanField(
        label=_('Edit before deploy ?'),
        help_text=_('Enable edit before deploy stack.'),
        required=False)

    attributes = {'class': 'switchable', 'data-slug': 'localsource'}
    choices = get_templates()
    template = forms.ChoiceField(label=_('Template'),
                                 choices=choices,
                                 widget=forms.Select(attrs=attributes),
                                 required=True)

    def __init__(self, request, *args, **kwargs):
        self.next_view = kwargs.pop('next_view')
        super(LocalTemplateStackForm, self).__init__(request, *args, **kwargs)

        if HEAT_LOCAL:
            for template in get_templates():
                attributes = create_upload_form_attributes(
                    'local',
                    '%s' % template[0],
                    _('Environment'))
                field = forms.ChoiceField(label=_('Environment'),
                                          choices=get_environments(
                                              template[0]),
                                          widget=forms.Select(
                                              attrs=attributes),
                                          required=False)
                self.fields["environment____%s" % template[0]] = field

    def clean(self):
        cleaned = super(LocalTemplateStackForm, self).clean()

        template_name = cleaned["template"]
        cleaned["template_data"] = get_template_data(template_name)
        cleaned["environment_data"] = get_environment_data(
            template_name, cleaned["environment____%s" % template_name])

        cleaned['stack_name'] = "%s_%s" % (
            cleaned["template"], cleaned["environment____%s" % cleaned["template"]])

        # Validate the template and get back the params.
        kwargs = {}
        kwargs['template'] = str(json.dumps(cleaned["template_data"], cls=CustomEncoder))

        try:
            validated = api.heat.template_validate(self.request, **kwargs)
            cleaned["parameters"] = validated
        except Exception as e:
            raise forms.ValidationError(unicode(e))

        return cleaned

    def create_kwargs(self, data):
        kwargs = {'parameters': data['parameters'],
                  'environment_data': data['environment_data'],
                  'template_data': str(json.dumps(data.get('template_data'), cls=CustomEncoder)),
                  'stack_name': data['stack_name']}
        if data.get('stack_id'):
            kwargs['stack_id'] = data['stack_id']
        return kwargs

    def update_param_defaults(self, data, params):

        _params = {}

        for key, dic in data["parameters"]["Parameters"].iteritems():
            if key in params:
                dic["Default"] = params[key]
                _params[key] = dic

        return _params

    def handle(self, request, data):

        params = data.get('environment_data')["parameters"]

        for param, key in data.get('template_data').iteritems():

            if isinstance(key, (list, dict)) and 'default' in key:
                params[param] = key['default']

        fields = {
            'stack_name': data.get('stack_name'),
            'template': str(json.dumps(data.get('template_data'), cls=CustomEncoder)),
            'environment': data.get('environment_data')["parameters"],
            'timeout_mins': data.get('timeout_mins'),
            'disable_rollback': not(data.get('enable_rollback')),
            'parameters': params,
        }

        # redirect to edit
        if data.pop("edit"):
            kwargs = self.create_kwargs(data)
            # NOTE (majklk) provide loaded parameters as defaults
            # maybe exist better way to do this
            kwargs["parameters"]["Parameters"] = self.update_param_defaults(data, params)
            # NOTE (gabriel): This is a bit of a hack, essentially rewriting this
            # request so that we can chain it as an input to the next view...
            # but hey, it totally works.
            request.method = 'GET'

            return self.next_view.as_view()(request, **kwargs)

        else:
            try:
                api.heat.stack_create(self.request, **fields)
                messages.success(request, _("Stack creation started."))
                return True
            except Exception:
                exceptions.handle(request)
