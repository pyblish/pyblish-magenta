import os
import pyblish.api

# Local library
import plugins


def setup():
    """Setup kit"""
    register_plugins()


def register_plugins():
    """Register accompanying plugins"""
    plugin_path = os.path.dirname(plugins.__file__)
    pyblish.api.register_plugin_path(plugin_path)
    print("pyblish_magenta: Registered %s" % plugin_path)
