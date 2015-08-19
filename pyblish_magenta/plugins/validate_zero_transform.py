import pyblish.api
from maya import cmds


class ValidateZeroTransform(pyblish.api.Validator):
    """Transforms can't have any values"""

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
        """Process all the nodes in the instance "objectSet" """
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
