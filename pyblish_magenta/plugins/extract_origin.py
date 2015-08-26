import os
import json
import pyblish_magenta.api


class ExtractOrigin(pyblish_magenta.api.Extractor):
    """Extract origin metadata from scene"""

    label = "Source files"
    families = ["metadata"]

    def process(self, instance):
        temp_dir = self.temp_dir(instance)
        temp_file = os.path.join(temp_dir, "origin.json")

        serialised = dict(
            instance.data("metadata"),
            references=list(instance)
        )

        self.log.info("Extracting %s" % serialised)
        with open(temp_file, "w") as f:
            json.dump(serialised, f, indent=2, sort_keys=True)

        self.log.info("Written to %s" % temp_file)
