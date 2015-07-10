import pyblish.api
import maya.cmds as cmds


def get_namespace(node_name):
    # ensure only node's name (not parent path)
    node_name = node_name.rsplit("|")[-1]
    # ensure only namespace
    return node_name.rpartition(":")[0]


class ValidateNoNamespace(pyblish.api.Validator):
    """Ensure the nodes don't have a namespace"""

    families = ['model']
    hosts = ['maya']
    category = 'cleanup'
    version = (0, 1, 0)
    label = 'No Namespaces'

    def process(self, instance):
        """Process all the nodes in the instance"""
        nodes = cmds.ls(instance, long=True)
        
        invalid = []
        for node in nodes:
            if get_namespace(node):
                invalid.append(node)
                
        if invalid:
            raise ValueError("Namespaces found: {0}".format(invalid))
                
    def repair(self, instance):
        """Remove all namespaces from the nodes in the instance"""
        # Get nodes with pymel since we'll be renaming them
        # Since we don't want to keep checking/sorting the hierarchy/fullpaths
        import pymel.core as pm
        nodes = pm.ls(instance)

        for node in nodes:
            namespace = node.namespace()
            if namespace:
                name = node.nodeName()
                node.rename(name[len(namespace):])
