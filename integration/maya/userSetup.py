import os
from maya import mel

try:
    import pyblish_magenta
    pyblish_magenta.setup()

except ImportError as e:
    print "pyblish_magenta: Could not load kit: %s" % e


# Set project
development_dir = os.environ.get("DEVELOPMENTDIR")

if development_dir:
    maya_dir = os.path.join(development_dir, "maya")

    if os.name == "nt":
        # MEL can't handle backslash
        maya_dir = maya_dir.replace("\\", "/")

    if not os.path.exists(maya_dir):
        os.makedirs(maya_dir)

    print("Setting Magenta development directory to: %s" % maya_dir)
    mel.eval('setProject \"' + maya_dir + '\"')
