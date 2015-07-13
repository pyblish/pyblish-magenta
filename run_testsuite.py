import os
import sys
from pyblish.vendor import nose

# Expose Pyblish Magenta to PYTHONPATH
path = os.path.dirname(__file__)
sys.path.insert(0, path)

import pyblish_magenta
pyblish_magenta.setup()

if __name__ == '__main__':
    argv = sys.argv[:]
    argv.extend(['--exclude=vendor', '--with-doctest', '--verbose'])
    nose.main(argv=argv)
