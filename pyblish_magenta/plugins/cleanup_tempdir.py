import shutil
import pyblish.api


class CleanupTempdir(pyblish.api.Plugin):
    """Remove temporary directories used during extraction"""
    label = "Cleanup"
    order = 99

    def process(self, instance):
        if not instance.has_data("extractDir"):
            return

        try:
            dirname = instance.data("extractDir")
            self.log.info("Cleaning up %s.." % dirname)
            shutil.rmtree(dirname)
            self.log.info("All clean")
        except IOError:
            self.log.info("Failed, there might be things lying around")
