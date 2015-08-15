import os
import json

import pyblish_magenta.plugin


class ExtractShaderLinks(pyblish_magenta.api.Extractor):
    """As JSON, create a mapping between mesh and shader"""

    label = "Shader links"
    hosts = ["maya"]
    families = ["lookdev"]

    def process(self, instance):
        self.log.info("Extracting links..")
        temp_dir = self.temp_dir(instance)
        temp_file = os.path.join(
            temp_dir, instance.data("name") + ".json")

        connections = instance.data("payload")
        with open(temp_file, "w") as f:
            self.log.info("Writing to disk: %s" % connections)
            json.dump(connections, f, indent=2, sort_keys=True)

        self.log.info("Links extracted successfully")
