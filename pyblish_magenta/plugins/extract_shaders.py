import os
import pyblish_maya
import pyblish_magenta.plugin


class ExtractShaders(pyblish_magenta.api.Extractor):
    """Output individual shaders"""

    label = "Shaders"
    hosts = ["maya"]
    families = ["lookdev"]

    def process(self, instance):
        from maya import cmds

        temp_dir = self.temp_dir(instance)
        temp_file = os.path.join(temp_dir, instance.data("name"))
        with pyblish_maya.maintained_selection():
            cmds.select(instance)
            cmds.file(temp_file,
                      force=True,
                      exportSelected=True,
                      constructionHistory=True,
                      type="mayaAscii")
