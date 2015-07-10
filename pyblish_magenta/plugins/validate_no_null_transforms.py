import pyblish.api
import maya.cmds as cmds


def has_shape_children(node):
    # Check if any descendants
    allDescendents = cmds.listRelatives(node, allDescendents=True, fullPath=True)
    if not allDescendents:
        return False

    # Check if there are any shapes at all
    shapes = cmds.ls(allDescendents, shapes=True)
    if not shapes:
        return False

    # Check if all descendent shapes are intermediateObjects;
    # if so we consider this node a null node and return False.
    if all(cmds.getAttr('{0}.intermediateObject'.format(x)) for x in shapes):
        return False

    return True


class ValidateNoNullTransforms(pyblish.api.Validator):
    """Ensure no null transforms are in the scene.

   We will consider transforms with only intermediate objects under it to be null transform as well. 
   
   .. note:: `listRelatives()` has a noIntermediate parameter; though it doesn't do anything
             when used together with the children parameter, but only with shapes=True)

    """

    families = ['model']
    hosts = ['maya']
    category = 'cleanup'
    version = (0, 1, 0)
    label = 'Empty/Null Transforms'

    def process(self, instance):
        """Process all the transform nodes in the instance """
        transforms = cmds.ls(instance, type='transform', long=True)
        
        invalid = []
        for transform in transforms:
            if not has_shape_children(transform):
                invalid.append(transform)
                
        if invalid:
            raise ValueError("Empty transforms found: {0}".format(invalid))
                
    def repair(self, instance):
        """Delete all null transforms.

        Note: If the node is used elsewhere (eg. connection to attributes or in history) deletion might mess up things.

        """
        
        member_nodes = cmds.sets(instance.name, q=1)
        transforms = cmds.ls(member_nodes, type='transform', long=True)
        
        invalid = []
        for transform in transforms:
            if not has_shape_children(transform):
                invalid.append(transform)
        
        if invalid:
            cmds.delete(invalid)
