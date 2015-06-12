
import pkgutil
from django.utils.importlib import import_module


def load_all_stuff(path):
    """recurively imports all members

    needed for rally stuff searching

    may take a long time

    """

    package = import_module(path)

    if hasattr(package, "__path__"):
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
            try:
                import_module(path + "." + modname)
            except ImportError:
                pass
            except Exception as e:
                raise e
            else:
                load_all_stuff(path + "." + modname)
