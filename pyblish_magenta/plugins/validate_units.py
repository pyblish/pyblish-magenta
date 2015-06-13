import pyblish.api


@pyblish.api.log
class ValidateUnits(pyblish.api.Validator):
    """ Validate the scene linear, angular and time units. """

    def process(self, context):
        units = context.data('units')
        if units and units != 'cm':
            raise RuntimeError("Scene linear units must be centimeters")

        units_angle = context.data('units_angle')
        if units_angle and units_angle != 'deg':
            raise RuntimeError("Scene angular units must be degrees")

        fps = context.data('fps')
        if fps and fps != 25.0:
            raise RuntimeError("Scene must be 25 FPS")