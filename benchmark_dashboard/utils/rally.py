
from __future__ import absolute_import

import glob
import sys
from os.path import basename

from django.conf import settings
from rally import exceptions
from yaml import load

RALLY_ROOT = getattr(settings, "RALLY_ROOT", "/srv/rally/scenarios/tasks")

SCENARIO_PATH = "scenarios"
CONTEXT_PATH = "contexts"

EXT = ".yaml"

EXT_MASK = "*%s" % EXT


class FailedToLoadTask(exceptions.RallyException):
    msg_fmt = ("Failed to load task")


def filename(path):
    """helper
    return filename without extension
    """
    return basename(path).split(".")[0]


def get_services(choices=True):
    """if choices is False return array of full path
    """

    path = "/".join([RALLY_ROOT, SCENARIO_PATH])

    templates = []
    for path in glob.glob("/".join([path, "*"])):
        name = basename(path).split("/")[0]
        templates.append((name, name.replace("_", " ").capitalize()))

    return sorted(templates)


def get_tasks(service_name=None, choices=True):
    """if choices is False return array of full path
    """

    if service_name:
        path = "/".join([RALLY_ROOT, SCENARIO_PATH, service_name])
    else:
        path = "/".join([RALLY_ROOT, SCENARIO_PATH])

    templates = []
    for path in glob.glob("/".join([path, EXT_MASK])):
        name = filename(path)
        templates.append((name, name.replace("_", " ").capitalize()))

    return sorted(templates)


def get_contexts(template_name=None):
    """return environments choices
    """
    path = "/".join([RALLY_ROOT, CONTEXT_PATH])

    environments = []

    join = [path, "*/*%s" % EXT]

    for path in glob.glob("/".join(join)):
        name = filename(path)
        environments.append((name, name.replace("_", " ").capitalize()))

    return sorted(environments)


def get_context_data(context_name):
    """return environments choices
    """
    path = "/".join([RALLY_ROOT, CONTEXT_PATH])

    data = {}

    join = [path, "*/*%s" % EXT]

    for context_path in glob.glob("/".join(join)):
        name = filename(context_path)
        if name == context_name:
            _path = "/".join([
                context_path
            ])

            try:
                f = open(_path, 'r')
                data = load(f)
            except Exception as e:
                raise e

    return data


def _load_task(task_file, task_args=None, task_args_file=None):
    """Load tasks template from file and render it with passed args.
    :param task_file: Path to file with input task
    :param task_args: JSON or YAML representation of dict with args that
                      will be used to render input task with jinja2
    :param task_args_file: Path to file with JSON or YAML representation
                           of dict, that will be used to render input
                           with jinja2. If both specified task_args and
                           task_args_file they will be merged. task_args
                           has bigger priority so it will update values
                           from task_args_file.
    :returns: Str with loaded and rendered task
    """

    def parse_task_args(src_name, args):
        try:
            kw = args and yaml.safe_load(args)
            kw = {} if kw is None else kw
        except yaml.parser.ParserError as e:
            print_invalid_header(src_name, args)

            raise TypeError()

        if not isinstance(kw, dict):
            print_invalid_header(src_name, args)
            raise TypeError()
        return kw

    try:
        kw = {}
        if task_args_file:
            with open(task_args_file) as f:
                kw.update(parse_task_args("task_args_file", f.read()))
        kw.update(parse_task_args("task_args", task_args))
    except TypeError:
        raise FailedToLoadTask()

    with open(task_file) as f:
        try:
            input_task = f.read()
            rendered_task = api.Task.render_template(input_task, **kw)
        except Exception as e:
            raise FailedToLoadTask()

        print(_("Input task is:\n%s\n") % rendered_task)
        try:
            return yaml.safe_load(rendered_task)
        except Exception as e:
            raise FailedToLoadTask()


def get_task_filename(name):
    """load and return scenario
    """

    path = "/".join([
        RALLY_ROOT,
        SCENARIO_PATH,
        "".join([name, EXT])
    ])

    return path


def get_task_data(name):
    """load and return scenario
    """

    path = "/".join([
        RALLY_ROOT,
        SCENARIO_PATH,
        "".join([name, EXT])
    ])

    try:
        f = open(path, 'r')
        data = load(f)
    except Exception, e:
        raise e

    return data


def get_environment_data(template_name, name):
    """load and return parameters data
    """

    path = "/".join([
        RALLY_ROOT,
        CONTEXT_PATH,
        template_name,
        "".join([name, EXT])
    ])

    try:
        f = open(path, 'r')
        data = load(f)
    except Exception, e:
        raise e

    return data
