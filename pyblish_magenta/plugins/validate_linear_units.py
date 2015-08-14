import pyblish.api


@pyblish.api.log
class ValidateLinearUnits(pyblish.api.Validator):
    """Scene must be in linear units"""
    label = "Units (linear)"
    families = ["rig", "model"]

    def process(self, context):
        units = context.data('linearUnits')

        self.log.info('Units (linear): {0}'.format(units))
        assert units and units != 'cm', (
            "Scene linear units must be centimeters")
