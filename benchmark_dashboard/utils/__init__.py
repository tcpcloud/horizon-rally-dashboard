
from benchmark_dashboard.utils.rally import get_services
from benchmark_dashboard.utils.rally import get_tasks
from benchmark_dashboard.utils.rally import get_contexts
from benchmark_dashboard.utils.rally import get_context_data
from benchmark_dashboard.utils.rally import get_task_filename
from benchmark_dashboard.utils.rally import get_task_data
from benchmark_dashboard.utils.rally import get_environment_data

__all__ = [
    "get_tasks",
    "get_contexts",
    "get_task_filename",
    "get_environment_data",
]

from json import JSONEncoder


class CustomEncoder(JSONEncoder):

    def default(self, obj):
        if set(['quantize', 'year']).intersection(dir(obj)):
            return str(obj)
        elif hasattr(obj, 'next'):
            return list(obj)
        return JSONEncoder.default(self, obj)
