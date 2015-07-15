import os as __os
import pyblish.api as __api
from . import plugins as __plugins

# API
from .lib import find_next_version


def setup():
    register_plugins()


def register_plugins():
    """Register accompanying plugins"""
    plugin_path = __os.path.dirname(__plugins.__file__)
    __api.register_plugin_path(plugin_path)
    print("pyblish_magenta: Registered %s" % plugin_path)


def deregister_plugins():
    """Deregister accompanying plugins"""
    plugin_path = __os.path.dirname(__plugins.__file__)
    __api.deregister_plugin_path(plugin_path)
    print("pyblish_magenta: Deregistered %s" % plugin_path)
