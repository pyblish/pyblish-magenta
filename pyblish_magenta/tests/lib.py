import contextlib
import pyblish.api
import pyblish_magenta


@contextlib.contextmanager
def magenta_plugins():
    pyblish_magenta.register_plugins()
    yield
    pyblish_magenta.deregister_plugins()


@contextlib.contextmanager
def registered(*plugins):
    """Temporarily register ONLY the supplied plug-ins

    Arguments:
        plugins (str): One or more names of plug-ins

    Example:
        >> with registered("CollectModel"):
        ..   # do things

    """

    pyblish.api.deregister_all_plugins()
    pyblish.api.deregister_all_paths()

    with magenta_plugins():
        for plugin in pyblish.api.discover():
            if plugin.id not in plugins:
                continue
            pyblish.api.register_plugin(plugin)

    try:
        yield
    finally:
        pyblish.api.deregister_all_plugins()


def errored(context):
    """Return True if context contains errors"""
    errored = list()
    for result in context.data("results"):
        if not result["error"]:
            continue
        errored.append(result["plugin"].id)
    return errored
