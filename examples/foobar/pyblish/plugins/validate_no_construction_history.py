import pyblish.api
from maya import cmds


class ValidateNoConstructionHistory(pyblish.api.Validator):
    """ Ensure no construction history exists on the nodes in the instance """
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Process all the nodes in the instance """
        invalid = []
        for node in instance:
            if cmds.listHistory(node, pruneDagObjects=True):
                invalid.append(node)
        if invalid:
            raise ValueError("Nodes found with construction history: {0}".format(invalid))

    def repair_instance(self, instance):
        """ Delete history on all nodes in the instance """
        cmds.delete(instance, channelHistory=True)