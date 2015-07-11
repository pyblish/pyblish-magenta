import os
import pyblish.api

# Local library
from . import plugins
from .lib import find_next_version


def setup():
    """Setup kit"""
    register_plugins()


def register_plugins():
    """Register accompanying plugins"""
    plugin_path = os.path.dirname(plugins.__file__)
    pyblish.api.register_plugin_path(plugin_path)
    print("pyblish_magenta: Registered %s" % plugin_path)


def deregister_plugins():
    """Register accompanying plugins"""
    plugin_path = os.path.dirname(plugins.__file__)
    pyblish.api.deregister_plugin_path(plugin_path)
    print("pyblish_magenta: Deregistered %s" % plugin_path)
