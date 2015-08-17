import pyblish.api


@pyblish.api.log
class ValidateUnitsAngular(pyblish.api.Validator):
    """Scene angular units must be in degrees"""
    label = "Units (angular)"
    families = ["rig", "model", "pointcache", "curves"]

    def process(self, context):
        units = context.data('angularUnits')

        self.log.info('Units (angular): {0}'.format(units))
        assert units and units == 'deg', (
            "Scene angular units must be degrees")
