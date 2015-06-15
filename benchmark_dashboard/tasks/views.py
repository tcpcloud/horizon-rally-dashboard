
from __future__ import print_function

import json
import logging
import os
import sys
import webbrowser
from operator import attrgetter
from tempfile import TemporaryFile

import jsonschema
import yaml
from benchmark_dashboard.api import rally
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse  # noqa
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from heat_server_templates.utils import (CustomEncoder, get_environment_data,
                                         get_environments, get_template_data,
                                         get_templates)
from horizon import exceptions, forms, tables, tabs
from horizon.utils import memoized
from oslo_utils import uuidutils
from rally import api, consts, db, exceptions, objects

from .forms import *
from .tables import TaskTable
from .utils import get_template

LOG = logging.getLogger(__name__)


class TaskIndexView(tables.DataTableView):
    table_class = TaskTable
    template_name = 'benchmark/tasks/index.html'

    def get_data(self):

        task_list = rally.tasks.list()

        return task_list


class DetailTaskView(generic.TemplateView):
    form_class = TaskStartForm
    success_url = reverse_lazy('horizon:benchmark:tasks:index')
    template_name = 'benchmark/tasks/detail.html'

    def get_context_data(self, **kw):

        template = get_template("tasks/report.mako")
        source, scenarios = rally.tasks.report(self.kwargs['task_id'])
        result = template.render(data=json.dumps(scenarios),
                                 source=json.dumps(source))
        return {'source': result}


class DownloadTaskReportView(generic.TemplateView):
    form_class = TaskStartForm
    template_name = 'benchmark/tasks/create.html'
    success_url = reverse_lazy('horizon:benchmark:tasks:index')

    def get(self, request, task_id):

        output = rally.tasks.plot(task_id)
        f = TemporaryFile()
        f.write(output)
        f.seek(0)
        response = HttpResponse(FileWrapper(f), content_type='application/zip')
        response['Content-Disposition'] = \
            'attachment; filename=report_%s.html' % task_id
        return response


class CreateTaskView(forms.ModalFormView):
    form_class = TaskStartForm
    template_name = 'benchmark/tasks/create.html'
    success_url = reverse_lazy('horizon:benchmark:tasks:index')

    def get_initial(self):
        return self.kwargs


class SelectScenarioView(forms.ModalFormView):
    form_class = TaskSelectForm
    template_name = 'benchmark/tasks/select.html'
    success_url = reverse_lazy('horizon:benchmark:tasks:index')

    def get_form_kwargs(self):
        kwargs = super(SelectScenarioView, self).get_form_kwargs()
        kwargs['next_view'] = CreateTaskView
        return kwargs
