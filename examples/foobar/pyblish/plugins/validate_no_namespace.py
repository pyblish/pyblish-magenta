import pyblish.api
import maya.cmds as cmds


def getNamespace(nodeName):
    # ensure only nodename
    nodeName = nodeName.rsplit("|")[-1]
    # ensure only namespace
    return nodeName.rpartition(":", 1)[0]


class ValidateNoNamespace(pyblish.api.Validator):
    """Ensure the nodes don't have a namespace """
    families = ['model']
    hosts = ['maya']
    category = 'cleanup'
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Process all the nodes in the instance """
        nodes = cmds.ls(instance, long=True)
        
        invalid = []
        for node in nodes:
            if getNamespace(node):
                invalid.append(node)
                
        if invalid:
            raise ValueError("Namespaces found: {0}".format(invalid))
                
    def repair_instance(self, instance):
        """ Remove all namespaces from the nodes in the instance """
        # Get nodes with pymel since we'll be renaming them (and we don't want keep checking/sorting hierarchy/fullpaths)
        import pymel.core as pm
        nodes = pm.ls(instance)

        for node in nodes:
            namespace = node.namespace()
            if namespace:
                name = node.nodeName()
                node.rename(name[len(namespace):])
