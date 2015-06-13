import os
from maya import mel

try:
    import pyblish_magenta
    pyblish_magenta.setup()

except ImportError as e:
    print "pyblish_magenta: Could not load kit: %s" % e


# Set project
development_dir = os.environ.get("DEVELOPMENTDIR")

if os.name == "nt":
    # MEL can't handle backslash
    development_dir = development_dir.replace("\\", "/")

if development_dir:
    print("Setting Magenta development directory to: %s" % development_dir)
    mel.eval('setProject \"' + development_dir + '\"')
