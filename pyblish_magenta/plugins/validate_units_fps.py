import pyblish.api


@pyblish.api.log
class ValidateUnitsFps(pyblish.api.Validator):
    """Validate the scene linear, angular and time units."""
    label = "Units (fps)"
    families = ["rig", "model", "pointcache", "curves"]

    def process(self, context):
        fps = context.data('fps')

        self.log.info('Units (time): {0} FPS'.format(fps))
        assert fps and fps == 25.0, "Scene must be 25 FPS"
