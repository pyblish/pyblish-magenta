import pyblish.api
from maya import cmds


class ValidateNoConstructionHistory(pyblish.api.Validator):
    """ Ensure no construction history exists on the nodes in the instance """
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)

    def process(self, instance):
        """Process all the nodes in the instance """
        if not instance:
            # Maya's listHistory errors out on an empty list so we return if not anything in the instance.
            return

        # quick check first
        if not cmds.listHistory(instance, pruneDagObjects=True):
            return

        # identify the invalid nodes
        invalid = []
        for node in instance:
            if cmds.listHistory(node, pruneDagObjects=True):
                invalid.append(node)
        if invalid:
            raise ValueError("Nodes found with construction history: {0}".format(invalid))

    def repair(self, instance):
        """ Delete history on all nodes in the instance """
        cmds.delete(instance, channelHistory=True)