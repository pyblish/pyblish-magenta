import pyblish.api
from maya import cmds


class ValidateNoIntermediateObjects(pyblish.api.Validator):
    """Ensure no intermediate objects are in the Context"""
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)
    label = "No Intermediate Objects"

    def list_intermediate_shapes(self, nodes):
        """Bugfixed wrapper to retrieve intermediate shapes

        .. note::
            Maya's `cmds.ls(instance, intermediateObjects=True, long=True)` also
            lists `displayLayer` as `intermediateObjects` even though they can
            only be shapes, which a `displayLayer` is not. So we filter beforehand.
        """
        shapes = cmds.ls(nodes, shapes=True, long=True)
        return cmds.ls(shapes, intermediateObjects=True, long=True)

    def process(self, instance):
        """Process all the intermediateObject nodes in the instance"""
        intermediate_objects = self.list_intermediate_shapes(instance)
        if intermediate_objects:
            raise ValueError("Intermediate objects found: {0}".format(intermediate_objects))
                
    def repair(self, instance):
        """Delete all intermediateObjects"""
        intermediate_objects = self.list_intermediate_shapes(instance)
        if intermediate_objects:
            future = cmds.listHistory(intermediate_objects, future=True)
            cmds.delete(future, ch=True)
            cmds.delete(intermediate_objects)
