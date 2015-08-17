"""Wrap bare alembic files into a Maya ASCII

Published assets are designed for Maya referencing, but alembics
have problems with this (need proof) and so they are first
embedded into a Maya scene file that is later referenced, in place
of referencing the bare alembic.

"""

import os
import json
import shutil
import tempfile
import subprocess
import contextlib
import pyblish.api


CREATE_NO_WINDOW = 0x08000000


class WrapAlembics(pyblish.api.Integrator):
    """Wrap alembic files with a Maya scene

    This plug-in launches Maya Standalone in a subprocess
    and wraps each pointcache instance into an additional
    Maya scene.

    Output from this subprocess is provided as DEBUG
    log records.

    """

    label = "Wrap Alembics"
    families = ["pointcache"]
    order = pyblish.api.Integrator.order + 0.1
    optional = True

    def process(self, context):
        paths = list()
        for instance in context:
            if instance.data("family") != "pointcache":
                continue

            integration_dir = instance.data("integrationDir")
            if not integration_dir:
                self.log.warning("%s did not have an integrationDir" % instance)
                continue

            paths.append(integration_dir)

        source = code.format(paths=json.dumps(paths))

        self.log.info("Running source in Maya Standalone: %s" % source)
        self.log.info("temp_file: %s" % temp_file)

        with temp_file(source) as filename:
            self.log.debug("Starting subprocess..")
            
            # Don't include Pyblish nor Magenta
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)

            popen = subprocess.Popen(["mayapy", filename],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     creationflags=CREATE_NO_WINDOW,
                                     env=environment)

            # Include full output, including any traceback
            for line in iter(popen.stdout.readline, b""):
                self.log.debug(line.strip())

            popen.communicate()  # Block till finished

            assert popen.returncode == 0, (
                "An error occured, see debug log messages for details")

            self.log.info("Alembics wrapped successfully")




code = r"""
# Wrap alembic in a Maya ASCII file
#
# This is written and run through maya.standalone
#
# Note:
#   Couldn't use inspect.getsource() on a function, due to a bug
#   in caching: https://bugs.python.org/issue1218234
#   Causing the getsource() to not return the latest update
#   on plug-in reload.
#

import os
import sys
import json

print("Initialising Maya..")
import pymel.core
from maya import cmds

cmds.loadPlugin('AbcImport', quiet=True)

paths = {paths}  # Provided at run-time

for path in paths:
    path = os.path.realpath(path)
    assert os.path.isdir(path)
    for alembic in os.listdir(path):
        alembic = os.path.join(path, alembic)
        if not alembic.endswith(".abc"):
            continue

        cmds.file(new=True, force=True)

        print("Importing %s" % alembic)
        cmds.AbcImport(alembic,
                       mode="import",
                       fitTimeRange=True,
                       setToStartFrame=True)

        # Sanity check
        for node in cmds.ls(type="AlembicNode"):
            print("%s.startFrame: %s" % (node, cmds.getAttr(node + ".startFrame")))

        wrapper = os.path.splitext(alembic)[0] + ".ma"
        wrapper = os.path.join(path, wrapper).replace("\\", "/")
        
        print("Exporting to %s" % wrapper)
        cmds.file(wrapper,
                  exportAll=True,
                  force=True,
                  type="mayaAscii",
                  constructionHistory=True)
        print("Exported successfully")

# Unless we explicitly exit, the process may
# throw a SegmentationFault.
sys.exit(0)

"""


@contextlib.contextmanager
def temp_file(source):
    tempdir = tempfile.mkdtemp()
    temppath = os.path.join(tempdir, "source.py")

    try:
        with open(temppath, "w") as f:
            f.write(source)
        yield temppath
    finally:
        shutil.rmtree(tempdir)