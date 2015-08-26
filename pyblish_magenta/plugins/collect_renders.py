import os
import pyblish.api


class CollectRenders(pyblish.api.Collector):
    """Collect images on disk, relative the current working directory"""

    hosts = ["maya", "standalone"]
    label = "Renders"
    order = pyblish.api.Collector.order + 0.1

    def process(self, context):
        """Rendered images are relative the working file

        For example, images rendered from the file myfile.mb
        are rendered into <dirname>/../images/myfile/

        Example:
            maya/
             scenes/
               myfile.mb        <-- Source file
             images/
               myfile/          <-- Destination renders
                 renderLayer1/
                  image1.exr

        """

        cwd = context.data("cwd")
        fname = context.data("currentFile")

        assert fname, ("Renders are based on the current file, "
                       "but none were found")

        fname, _ = os.path.splitext(os.path.basename(fname))

        self.log.debug("Current working directory: %s" % cwd)
        self.log.debug("Current file: %s" % fname)

        layers_dir = os.path.realpath(
            os.path.join(cwd, "maya", "images", fname))

        try:
            layers = os.listdir(layers_dir)
        except OSError:
            return self.log.debug("No renders found for %s" % fname)
        if not layers:
            return self.log.debug("No renders found for %s" % fname)

        for layer in layers:
            self.log.info("Found layer \"%s\"" % layer)

            instance = context.create_instance(layer, family="renderlayer")
            instance.set_data("path", os.path.join(layers_dir, layer))

            root = os.path.join(layers_dir, layer)
            for child in os.listdir(root):
                self.log.info("Adding /%s" % child)
                instance[:] = os.path.join(root, child)
