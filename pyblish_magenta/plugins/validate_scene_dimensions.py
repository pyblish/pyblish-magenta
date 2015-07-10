import pyblish.api
from maya import cmds


class ValidateSceneDimensions(pyblish.api.Validator):
    """Ensure objects are not immensely huge and not positioned in the far far corners of the 3D space."""

    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    optional = True
    version = (0, 1, 0)
    label = "Scene Dimensions (prevent huge object)"

    __far = 1e5  # what we consider the far distance

    def process(self, instance):
        """Process all the nodes in the instance"""
        # TODO: Maybe swap transform type with dagNode type?
        transforms = cmds.ls(instance, type='transform', long=True)

        invalid = []
        for node in transforms:
            bounding_box = cmds.xform(node, q=1, worldSpace=True, boundingBox=True)
            if any(x < -self.__far for x in bounding_box[:3]) or any(x > self.__far for x in bounding_box[3:]):
                invalid.append(node)

        if invalid:
            raise ValueError("Nodes found far away or of big size ('{far}'): {0}".format(invalid, far=self.__far))