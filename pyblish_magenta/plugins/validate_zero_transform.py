import pyblish.api
from maya import cmds


class ValidateZeroTransform(pyblish.api.Validator):
    """Transforms can't have any values

    To solve this issue, try freezing the transforms. So long
    as the transforms, rotation and scale values are zero,
    you're all good.

    """

    families = ["model"]
    hosts = ["maya"]
    category = "geometry"
    version = (0, 1, 0)
    label = "Zero Transform"

    __identity = [1.0, 0.0, 0.0, 0.0,
                  0.0, 1.0, 0.0, 0.0,
                  0.0, 0.0, 1.0, 0.0,
                  0.0, 0.0, 0.0, 1.0]
    __tolerance = 1e-30

    def process(self, instance):
        """Process all the nodes in the instance "objectSet"

        This is the same as checking:
        - translate == [0, 0, 0] and rotate == [0, 0, 0] and
          scale == [1, 1, 1] and shear == [0, 0, 0]

        .. note::
            This will also catch camera transforms if those
            are in the instances.

        """

        transforms = cmds.ls(instance, type="transform")

        invalid = []
        for transform in transforms:
            mat = cmds.xform(transform, q=1, matrix=True, objectSpace=True)
            if not all(abs(x-y) < self.__tolerance
                       for x, y in zip(self.__identity, mat)):
                invalid.append(transform)

        if invalid:
            raise ValueError("Nodes found with transform "
                             "values: {0}".format(invalid))
