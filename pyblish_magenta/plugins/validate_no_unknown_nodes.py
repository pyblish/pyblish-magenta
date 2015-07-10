import pyblish.api
from maya import cmds


class ValidateNoUnknownNodes(pyblish.api.Validator):
    """Checks to see if there are any unknown nodes in the scene.
        This often happens if nodes from plug-ins are used but are not available on this machine.

        Note: Some studios use unknown nodes to store data on (as attributes) because it's a lightweight node.

    """

    families = ['model', 'layout']
    hosts = ['maya']
    category = 'cleanup'
    optional = True
    version = (0, 1, 0)
    label = "Unknown Nodes"

    def process(self, instance):
        """Process all the nodes in the instance"""
        unknown_nodes = cmds.ls(instance, type='unknown')
        if unknown_nodes:
            raise ValueError("Unkown nodes found: {0}".format(unknown_nodes))