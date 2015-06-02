import os
import pyblish.api


@pyblish.api.log
class SelectConceptArt(pyblish.api.Selector):
  def process(self, context):
    self.log.info("Selecting concept art..")

    cwd = context.data("cwd")
    for fname in os.listdir(cwd):
        if fname.lower().endswith(".png"):
            name = os.path.basename(fname.rsplit(".", 1)[0])

            self.log.info("Creating instance: %s" % name)
            instance = context.create_instance(name)

            # Capture certain characteristics for validation
            instance.set_data("family", "conceptArt")
            instance.set_data("path", os.path.join(context.data("cwd"), fname))
            instance.set_data("bytes", os.stat(fname).st_size)
