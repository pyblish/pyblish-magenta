import pyblish.api
from maya import cmds


class ValidateReferencesOnly(pyblish.api.Validator):
    """ Validate that all nodes are referenced nodes. """
    families = ['layout']
    hosts = ['maya']
    category = 'layout'
    optional = True
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Process all the nodes in the instance 'objectSet' """
        member_nodes = cmds.sets(instance.name, q=1)
        referenced_nodes = cmds.ls(member_nodes, referencedNodes=True, long=True)

        if len(referenced_nodes) != len(member_nodes):
            # Now we know some nodes are not referenced
            # Let's compare by long names
            member_nodes = cmds.ls(member_nodes, long=True)
            referenced_nodes_lookup = frozenset(referenced_nodes)

            non_referenced_nodes = [node for node in member_nodes if not node in referenced_nodes_lookup]
            if non_referenced_nodes:
                raise ValueError("Non-referenced nodes found: {0}".format(non_referenced_nodes))

        # Another way of doing it (which might be slower (untested))
        #invalid = []
        #for node in member_nodes:
        #    if not cmds.referenceQuery(isNodeReferenced=node):
        #        invalid.append(node)

