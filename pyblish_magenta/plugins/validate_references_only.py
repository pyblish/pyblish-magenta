import pyblish.api
from maya import cmds


class ValidateReferencesOnly(pyblish.api.Validator):
    """Validate that all nodes are referenced nodes."""
    families = ['layout']
    hosts = ['maya']
    category = 'layout'
    optional = True
    version = (0, 1, 0)
    label = 'Ensure References Only'

    def process(self, instance):
        """Process all the nodes in the instance"""
        referenced_nodes = cmds.ls(instance, referencedNodes=True, long=True)

        if len(referenced_nodes) != len(instance):
            # Now we know some nodes are not referenced
            # Let's compare by long names
            member_nodes = cmds.ls(instance, long=True)
            referenced_nodes_lookup = frozenset(referenced_nodes)

            non_referenced_nodes = [node for node in member_nodes if node not in referenced_nodes_lookup]
            if non_referenced_nodes:
                raise ValueError("Non-referenced nodes found: {0}".format(non_referenced_nodes))

        # Another way of doing it (which might be slower (untested))
        # invalid = []
        # for node in member_nodes:
        #    if not cmds.referenceQuery(isNodeReferenced=node):
        #        invalid.append(node)

