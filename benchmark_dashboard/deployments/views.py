# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import print_function

import logging

from django.utils.translation import ugettext_lazy as _
from horizon import exceptions, forms, tables, tabs


from benchmark_dashboard.api import rally

from .tables import DeploymentTable

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = DeploymentTable
    template_name = 'benchmark/deployments/index.html'

    def get_data(self):

        deployment_list = rally.deployments.list()

        return deployment_list
