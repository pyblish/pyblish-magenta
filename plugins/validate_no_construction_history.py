import pyblish.api
from maya import cmds


class ValidateNoConstructionHistory(pyblish.api.Validator):
    """Ensure no construction history exists in for the instances """
    families = ['modeling']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Process all the nodes in the instance  'objectSet' """
        member_nodes = cmds.sets(instance.name, q=1)
        invalid = []
        for node in member_nodes:
            if cmds.listHistory(node, pruneDagObjects=True):
                invalid.append(node)
        if invalid:
            raise ValueError("Nodes found with construction history: {0}".format(invalid))

            
    def repair_instance(self, instance):
        member_nodes = cmds.sets(instance.name, q=1)
        cmds.delete(member_nodes, channelHistory=True)