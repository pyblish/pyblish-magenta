import shutil
import pyblish.api


class IntegrateCleanup(pyblish.api.Integrator):
    """Remove temporary directories used during extraction"""
    label = "Cleanup"
    order = 99

    def process(self, instance):
        try:
            shutil.rmtree(instance.data("extractDir"))
        except IOError:
            pass
