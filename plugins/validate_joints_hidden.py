import pyblish.api
from maya import cmds


def isVisible(node, displayLayer=True, intermediateObject=True, parentHidden=True, visibility=True):
    """
    Returns whether a node is hidden by one of the following methods (if parameter is True):
    - The node exists (always checked)
    - The node must be a dagNode (always checked)
    - The node's visibility is off.
    - The node is set as intermediate Object.
    - The node is in a disabled displayLayer.
    - Whether any of its parent nodes is hidden.

    Roughly based on: http://ewertb.soundlinker.com/mel/mel.098.php

    :return: Whether the node is visible in the scene
    :rtype: bool
    """
    # Only existing objects can be visible
    if not cmds.objExists(node):
        return False

    # Only dagNodes can be visible
    if not cmds.objectType(node, isAType='dagNode'):
        return False

    if visibility:
        if not cmds.getAttr('{0}.visibility'.format(node)):
            return False

    if intermediateObject and cmds.objectType(node, isAType='shape'):
        if not cmds.getAttr('{0}.intermediateObject'.format(node)):
            return False

    if displayLayer:
        # Note that the display layer set overrideEnabled and overrideVisibility on the node.
        if cmds.attributeQuery('overrideEnabled', node=node, exists=True):
            if cmds.getAttr('{0}.overrideEnabled'.format(node)) and cmds.getAttr('{0}.overrideVisibility'.format(node)):
                return False

    if parentHidden:
        parent = cmds.listRelatives(node, parent=True)[0]
        if parent:
            if not isVisible(parent, displayLayer=displayLayer, intermediateObject=False,
                                     parentHidden=parentHidden, visibility=visibility):
                return False

    return True


class ValidateJointsHidden(pyblish.api.Validator):
    """ Validate all joints are hidden.

        .. note::
            We don't count a disabled displayLayer for the joints as hidden joints.
    """
    families = ['rig']
    hosts = ['maya']
    category = 'rig'
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Process all the nodes in the instance 'objectSet' """
        member_nodes = cmds.sets(instance.name, q=1)
        joints = cmds.ls(member_nodes, type='joint', dag=True, long=True)

        invalid = []
        for joint in joints:
            if isVisible(joint, displayLayer=False):
                invalid.append(joint)

        if invalid:
            raise ValueError("Meshes found with lamina faces: {0}".format(invalid))