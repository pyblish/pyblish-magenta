á# stdlib
import os

# maya & pyblish lib
import pyblish.api
import maya.cmds as mc

# local lib
from pyblish_magenta.utils.maya.exporter import MayaExporter
import pyblish_magenta.schema


@pyblish.api.log
class ExtractModel(pyblish.api.Extractor):
    """ Exports all nodes """
    hosts = ["maya"]
    families = ["model"]

    def process(self, instance):

        # Get instance data
        data = {'root': instance.data('root'),
                'container': instance.data('container'),
                'asset': instance.data('asset')}

        # Get output directory
        schema = pyblish_magenta.schema.load()
        dir_path = schema.get("model.asset").format(data)

        # Get output filename
        filename = "{0}.ma".format(instance.name)

        path = os.path.join(dir_path, filename)

        export_nodes = mc.ls(instance, long=True)

        if not export_nodes:
            raise RuntimeError("Nothing to export")

        MayaExporter.export(path, export_nodes,
                            preserveReferences=False, constructionHistory=False,
                            expressions=False, channels=False,
                            constraints=False, shader=False,
                            displayLayers=False, objectSets=False)

        self.log.info("Extracted instance '{0}' to: {1}".format(instance.name, path))