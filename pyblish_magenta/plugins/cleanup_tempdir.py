import shutil
import pyblish.api


class CleanupTempdir(pyblish.api.Plugin):
    """Remove temporary directories used during extraction"""
    label = "Cleanup"
    order = 99

    def process(self, context):
        try:
            shutil.rmtree(context.data("extractDir"))
        except IOError:
            pass
