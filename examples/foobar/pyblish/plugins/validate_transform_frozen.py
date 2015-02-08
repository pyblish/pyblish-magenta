import pyblish.api
from maya import cmds


class ValidateTransformFrozen(pyblish.api.Validator):
    """ Validate all transforms are freeze transformed by checking for objectSpace identity matrix.

        This is the same as checking:
        - translate == [0, 0, 0] and rotate == [0, 0, 0] and scale == [1, 1, 1] and shear == [0, 0, 0]

        .. note::
            This will also catch camera transforms if those are in the instances.
    """
    # TODO: Check if this suffer from floating point precision errors. If so we need to implement a set tolerance.

    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)

    __identity = [1.0, 0.0, 0.0, 0.0,
                  0.0, 1.0, 0.0, 0.0,
                  0.0, 0.0, 1.0, 0.0,
                  0.0, 0.0, 0.0, 1.0]

    def process_instance(self, instance):
        """Process all the nodes in the instance 'objectSet' """
        transforms = cmds.ls(instance, type='transform')

        invalid = []
        for transform in transforms:
            mat = cmds.xform(transform, q=1, matrix=True, objectSpace=True)
            if self.__identity != mat:
                invalid.append(transform)

        if invalid:
            raise ValueError("Nodes found with unfrozen transforms: {0}".format(invalid))