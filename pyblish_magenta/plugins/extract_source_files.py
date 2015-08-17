import os
import json
import pyblish_magenta.api


class ExtractSourceFiles(pyblish_magenta.api.Extractor):
    """Extract source references used in the scene"""

    label = "Source files"
    families = ["metadata"]

    def process(self, instance):
        temp_dir = self.temp_dir(instance)
        temp_file = os.path.join(temp_dir, "source_files.json")
        self.log.info("Writing source files to %s" % temp_file)
        
        serialised = [f for f in instance]

        with open(temp_file, "w") as f:
            json.dump(serialised, f)
