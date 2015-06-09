
import os
import mako.exceptions
import mako.lookup
import mako.template


templates_dir = os.path.join(os.path.dirname(__file__), "templates")

lookup_dirs = [templates_dir,
               os.path.abspath(os.path.join(templates_dir, "..", "..", ".."))]

lookup = mako.lookup.TemplateLookup(directories=lookup_dirs)


def get_template(template_path):
    return lookup.get_template(template_path)
