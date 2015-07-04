import pyblish.api


@pyblish.api.log
class ValidateUnits(pyblish.api.Validator):
    """Validate the scene linear, angular and time units."""
    label = "Scene Units"

    def process(self, context):

        units = context.data('units')
        units_angle = context.data('units_angle')
        fps = context.data('fps')

        self.log.info('Units (linear): {0}'.format(units))
        self.log.info('Units (angular): {0}'.format(units_angle))
        self.log.info('Units (time): {0} FPS'.format(fps))

        if units and units != 'cm':
            raise RuntimeError("Scene linear units must be centimeters")

        if units_angle and units_angle != 'deg':
            raise RuntimeError("Scene angular units must be degrees")

        if fps and fps != 25.0:
            raise RuntimeError("Scene must be 25 FPS")