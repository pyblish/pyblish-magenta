# stdlib
import os

# maya & pyblish lib
import pyblish.api
import maya.cmds as mc

# local lib
from pyblish_magenta.utils.maya.exporter import MayaExporter
import pyblish_magenta.plugin


@pyblish.api.log
class ExtractModel(pyblish_magenta.plugin.Extractor):
    """ Exports all nodes """
    hosts = ["maya"]
    families = ["model"]
    optional = True

    def process(self, instance):

        # Define extract output file path
        dir_path = self.temp_dir(instance)
        filename = "{0}.ma".format(instance.name)
        path = os.path.join(dir_path, filename)

        # Define extract nodes
        export_nodes = mc.ls(instance, long=True)
        if not export_nodes:
            raise RuntimeError("Nothing to export")

        # Perform extraction
        MayaExporter.export(path, export_nodes,
                            preserveReferences=False, constructionHistory=False,
                            expressions=False, channels=False,
                            constraints=False, shader=False,
                            displayLayers=False, objectSets=False,
                            smoothPreview=False)

        self.log.info("Extracted instance '{0}' to: {1}".format(instance.name, path))