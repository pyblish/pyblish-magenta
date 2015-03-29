import os
import pyblish.api


@pyblish.api.log
class ExtractShaders(pyblish.api.Extractor):
    """
        Exports all nodes
    """
    hosts = ["maya"]
    families = ["lookdev"]

    def process_instance(self, instance):
        path = instance.context.data("current_file")
        for level in range(7):
            path = os.path.dirname(path)

        self.log.info("Root of project @ %s" % path)

        path = os.path.join(path,
                            "assets",
                            "model",
                            "characters",
                            instance.name,
                            "shaders")

        self.log.info("Looking for destination directory @ %s"
                      % path)

        self.log.info("About to extract..")
        for shader in instance:
            if not shader.type == "lambert":
                continue

            self.log.info("Extracting %s to %s" % (shader.name, path))
