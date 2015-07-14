import os
import sys
import nose

# Expose Pyblish Magenta to PYTHONPATH
path = os.path.dirname(__file__)
sys.path.insert(0, path)

if __name__ == '__main__':
    argv = sys.argv[:]
    argv.extend(['--exclude=vendor', '--verbose'])
    nose.main(argv=argv)
