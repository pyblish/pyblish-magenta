import pyblish.api
from maya import cmds


class ValidateNoTransformZeroScale(pyblish.api.Validator):
    """Validate there are no transforms with zero scale.
    Especially in modeling that would be a rather useless transform. :)

    .. note:
        Consider this more of a validation example, because most pipelines will check for frozen transforms
        anyway which will also take care of validating a zero scale case. Nevertheless since object's can
        hardly be found in the viewport when they would have zero scale this is a good example for automated
        validation.

    """

    # TODO: Check if this suffer from floating point precision errors. If so we need to implement a set tolerance.

    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)
    label = "Transform Zero Scale"

    __epsilon = 1e-5

    def process(self, instance):
        """Process all the nodes in the instance"""
        transforms = cmds.ls(instance, type='transform')

        invalid = []
        for transform in transforms:
            scale = cmds.xform(transform, q=1, scale=True, objectSpace=True, relative=True)
            if any(abs(x) < self.__epsilon for x in scale):
                invalid.append(transform)

        if invalid:
            raise ValueError("Nodes found with (close to) zero scale: {0}".format(invalid))