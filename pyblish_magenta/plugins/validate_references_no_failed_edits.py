import pyblish.api
from maya import cmds


class ValidateReferencesNoFailedEdits(pyblish.api.Validator):
    """Validate that all referenced nodes' reference nodes don't have failed reference edits.

        Failed reference edits can happen if you apply a change to a referenced object in the scene and then change
        the source of the reference (that actual file) to remove the object. The reference edit can't be applied to
        the object because it doesn't exist anymore, hence a 'failed reference edit'.
        It's a thing most artists won't check but in large sets this could bloat file sizes unnecessarily.

        .. note::
            The terminology here can easily confuse you.
            reference node: The node that is the actual reference containing the nodes (type: referenceNode)
            referenced nodes: The nodes contained within the reference (type: any type of nodes)

    """

    families = ['layout']
    hosts = ['maya']
    category = 'layout'
    optional = True
    version = (0, 1, 0)
    label = 'References Failed Edits'

    def process(self, instance):
        """Process all the nodes in the instance"""

        referenced_nodes = cmds.ls(instance, referencedNodes=True, long=True)
        if not referenced_nodes:
            return

        # Get reference nodes from referenced nodes (note that reference_nodes != referenced_nodes)
        reference_nodes = set()
        for node in referenced_nodes:
            reference_node = cmds.referenceQuery(node, referenceNode=True)
            if reference_node:
                reference_nodes.add(reference_node)

        # Check for failed edits on each reference node.
        invalid = []
        for reference_node in reference_nodes:
            failed_edits = cmds.referenceQuery(reference_node, editNodes=True, failedEdits=True, successfulEdits=True)
            if failed_edits:
                invalid.append(reference_node)

        if invalid:
            raise ValueError("Reference nodes found with failed reference edits: {0}".format(invalid))

