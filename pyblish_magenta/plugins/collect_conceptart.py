import os
import pyblish.api


@pyblish.api.log
class CollectConceptArt(pyblish.api.Collector):
    """Collect Concept Art files from the current work directory.

    Any `.png` files in the `cwd` are considered to be artwork.

    """

    def process(self, context):
        self.log.info("Selecting concept art..")

        cwd = os.getcwd()
        for fname in os.listdir(cwd):
            if fname.lower().endswith(".png"):
                name = os.path.basename(fname.rsplit(".", 1)[0])

                self.log.info("Creating instance: %s" % name)
                instance = context.create_instance(name)

                # Capture certain characteristics for validation
                instance.set_data("family", "conceptArt")
                instance.set_data("path", os.path.join(
                                  context.data("cwd"), fname))
                instance.set_data("bytes", os.stat(fname).st_size)
