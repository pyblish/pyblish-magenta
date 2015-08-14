import os
import re
import pyblish.api

from . import plugins


PLUGINS_PATH = os.path.dirname(plugins.__file__)
PLUGIN_PATHS = [PLUGINS_PATH]


def find_next_version(versions):
    """Return next version from list of versions

    If multiple numbers are found in a single version,
    the last one found is used. E.g. (6) from "v7_22_6"

    Arguments:
        versions (list): Version numbers as string

    Example:
        >>> find_next_version(["v001", "v002", "v003"])
        4
        >>> find_next_version(["1", "2", "3"])
        4
        >>> find_next_version(["v1", "v0002", "verision_3"])
        4
        >>> find_next_version(["v2", "5_version", "verision_8"])
        9
        >>> find_next_version(["v2", "v3_5", "_1_2_3", "7, 4"])
        6
        >>> find_next_version(["v010", "v011"])
        12

    """

    highest_version = 0
    for version in versions:
        matches = re.findall(r"\d+", version)

        if not matches:
            continue

        version = int(matches[-1])
        if version > highest_version:
            highest_version = version

    return highest_version + 1

PLUGINS_PATH = os.path.dirname(plugins.__file__)
PLUGIN_PATHS = [PLUGINS_PATH]

for subdir in ("collectors", "extractors", "validators", "integrators"):
    PLUGIN_PATHS.append(os.path.join(PLUGINS_PATH, subdir))


def setup():
    register_plugins()


def register_plugins():
    """Register accompanying plugins"""
    for path in PLUGIN_PATHS:
        pyblish.api.register_plugin_path(path)

    print("pyblish_magenta: Registered plug-ins")


def deregister_plugins():
    """Deregister accompanying plugins"""
    for path in PLUGIN_PATHS:
        pyblish.api.deregister_plugin_path(path)

    print("pyblish_magenta: Deregistered plug-ins")
