import pyblish.api
from maya import cmds


class ValidateNoIntermediateObjects(pyblish.api.Validator):
    """ Ensure no intermediate objects are in the Context """
    families = ['modeling']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Process all the nodes in the instance 'objectSet' """
        member_nodes = cmds.sets(instance.name, q=1)

        intermediate_objects = cmds.ls(member_nodes, dag=1, intermediateObjects=True, long=True)
        if intermediate_objects:
            raise ValueError("Intermediate objects found: {0}".format(intermediate_objects))
                
    def repair_instance(self, instance):
        """ Delete all intermediateObjects """
        member_nodes = cmds.sets(instance.name, q=1)

        intermediate_objects = cmds.ls(member_nodes, dag=1, intermediateObjects=True, long=True)
        if intermediate_objects:
            future = cmds.listHistory(intermediate_objects, future=True)
            cmds.delete(future, ch=True)
            cmds.delete(intermediate_objects)
