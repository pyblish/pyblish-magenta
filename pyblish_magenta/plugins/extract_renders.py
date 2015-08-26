import os
import shutil
import pyblish_magenta.api


class ExtractRenders(pyblish_magenta.api.Extractor):
    label = "Renders"
    families = ["renderlayer"]

    def process(self, instance):
        temp_dir = self.temp_dir(instance)

        path = instance.data("path")

        self.log.info("Extracting \"%s\" to \"%s\"" % (path, temp_dir))
        for layer in os.listdir(path):
            src = os.path.join(path, layer)
            dst = os.path.join(temp_dir, layer)
            shutil.copytree(src, dst)

        instance.set_data("extractDir", temp_dir)
        self.log.info("Written successfully")
