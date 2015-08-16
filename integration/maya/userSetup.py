from __future__ import absolute_import

import os
import maya.mel
import maya.utils

from PySide.QtGui import QApplication

try:
    import pyblish_magenta.api
    pyblish_magenta.api.setup()

    import pyblish_magenta.utils.maya.uuid
    pyblish_magenta.utils.maya.uuid.register_callback()

except ImportError as e:
    print "pyblish_magenta: Could not load kit: %s" % e


def set_project():
    """The current working directory is assumed to be the Maya Project"""
    maya_dir = os.path.join(os.getcwd(), "maya")

    if not os.path.exists(maya_dir):
        os.makedirs(os.path.join(maya_dir, "scenes"))

    if os.name == "nt":
        # MEL can't handle backslash
        maya_dir = maya_dir.replace("\\", "/")

    print("Setting development directory to: %s" % maya_dir)
    maya.mel.eval('setProject \"' + maya_dir + '\"')


def distinguish():
    """Distinguish GUI from other projects

    This adds a green line to the top of Maya's GUI

    """

    QApplication.instance().setStyleSheet("""
    QMainWindow > QMenuBar {
      border-bottom: 1px solid lightgreen;
    }
    """)


set_project()
maya.utils.executeDeferred(distinguish)
