import os
import json
import shutil
import inspect
import tempfile
import subprocess
import contextlib
import pyblish.api


CREATE_NO_WINDOW = 0x08000000


class WrapAlembic(pyblish.api.Extractor):
    """Wrap alembic files in a Maya scene

    This plug-in launches Maya Standalone in a subprocess
    and wraps each pointcache instance into an additional
    Maya scene.

    Output from this subprocess is provided as DEBUG
    log records.

    """

    families = ["pointcache"]
    order = pyblish.api.Extractor.order + 0.1

    def process(self, context):

        tempdir = tempfile.mkdtemp()
        temppath = os.path.join(tempdir, "code.py")

        paths = list()
        for instance in context:
            if instance.data("family") != "pointcache":
                continue
            extract_dir = instance.data("extractDir")
            if not extract_dir:
                self.log.warning("%s did not have an extractDir" % instance)
                continue

            paths.append(extract_dir)

        source = "%s\ncode()" % inspect.getsource(code)
        source = source.format(paths=json.dumps(paths))

        self.log.info("Running source in Maya Standalone: %s" % source)
        self.log.info("temp_file: %s" % temp_file)

        with temp_file(source) as filename:
            self.log.debug("Starting subprocess..")
            popen = subprocess.Popen(["mayapy", filename],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     creationflags=CREATE_NO_WINDOW)
            for line in iter(popen.stdout.readline, b""):
                self.log.debug(line.strip())
            popen.communicate()  # Block till finished
            assert popen.returncode == 0, (
                "An error occured, see debug log messages for details")


def code():
    """Wrap `alembic` in a Maya ASCII file

    DO NOT RUN DIRECTLY.

    This function is serialised, written and run through
    maya.standalone in the plug-in below

    """

    import json

    from maya import cmds
    from maya import standalone

    print("Initialising Maya..")
    standalone.initialize()

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
            cmds.AbcImport(alembic, mode="open")

            wrapper = os.path.splitext(alembic)[0] + ".ma"
            wrapper = os.path.join(path, wrapper).replace("\\", "/")
            
            print("Exporting to %s" % wrapper)
            cmds.file(rename=wrapper)

            cmds.file(wrapper, exportAll=True, force=True, type="mayaAscii")
            print("Exported successfully")

    os.exit(0)


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