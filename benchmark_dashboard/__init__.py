
# autoinclude
# proper way for this is enabled but it makes additional requirements for enabling
from horizon import conf

conf.HORIZON_CONFIG['angular_modules'] = conf.HORIZON_CONFIG['angular_modules'] + ['rally-benchmark']
conf.HORIZON_CONFIG['js_files'] = conf.HORIZON_CONFIG['js_files'] + ['benchmark/js/report.js']

from openstack_dashboard import settings

settings.COMPRESS_OFFLINE_CONTEXT['HORIZON_CONFIG'] = conf.HORIZON_CONFIG
