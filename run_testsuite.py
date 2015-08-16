import os
import sys
import logging

import nose

# Expose Pyblish Magenta to PYTHONPATH
path = os.path.dirname(__file__)
sys.path.insert(0, path)

# Plug-ins produce a lot of messages,
# mute these during tests.
logging.disable(logging.CRITICAL)

if "maya" in sys.executable.lower():
    __import__("pyblish_maya").setup()

elif "houdini" in sys.executable.lower():
    __import__("pyblish_houdini").setup()

elif "nuke" in sys.executable.lower():
    __import__("pyblish_nuke").setup()


if __name__ == "__main__":
    argv = sys.argv[:]
    argv.extend(['--exclude=vendor', '--verbose'])
    nose.main(argv=argv)
    os._exit(0)
