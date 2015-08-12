# stdlib
from collections import OrderedDict, Counter
from itertools import izip, repeat

# maya lib
from maya import cmds


def get_dag_order(filter_shapes=True):
    """
     Returns an OrderedDictionary for all nodes where key is full node name and value is the order-index for that node under its current parent.

     :param filter_shapes: Whether to filter shapes from the returned dictionary.
                          If you have shapes next to transforms in your hierarchy this might become an issue.
     :type filter_shapes: bool

     :returns: Dictionary in format of {"nodeFullPathName": index}
     :rtype: collections.OrderedDictionary

     .. note::
        (Maya Bug) You can't use mc.ls(type="transform") to filter directly as it changes the returned order.
        The workaround is to get the full ls() list first and perform mc.ls(lst, type="transform") afterwards.

        Though with the current algorithm/functionality we can't use a pre-filtered list without removing
        assumptions in this algorithm. We could allow for filtering, but it will be slower than the current
        implementation.
    """
    dag = cmds.ls(dag=True, long=True)

    # Turn the node list into an ordered dictionary (with None as temp value)
    dag = OrderedDict(izip(dag, repeat(None)))

    # Remove the shapes from the dictionary
    if filter_shapes:
        for shape in cmds.ls(shapes=True, long=True):
            # We use `dict.pop(index, None)` instead of
            # `del dict[index]` as the key might not exist.
            dag.pop(shape, None)

    # For each calculate amount of parents
    # Since everything listed so far is in order we count it ourselves
    hierarchy_counter = Counter()
    for node in dag:
        parent = node.rpartition("|")[0]
        dag[node] = hierarchy_counter[parent]
        hierarchy_counter[parent] += 1

    return dag


def is_driven(node_attr):
    return bool(cmds.listConnections(node_attr,
                                     destination=True,
                                     source=False))


def is_visible(node,
               display_layer=True,
               intermediate_object=True,
               parent=True,
               visibility=True,
               frames=None):
    """Returns whether a node is at least one frame visible at the frames.

    Checks the following conditions if parameters are True:
    - The node exists (always checked)
    - The node must be a dagNode (always checked)
    - The node's visibility is off.
    - The node is set as intermediate Object.
    - The node is in a disabled displayLayer.
    - Whether any of its parent nodes is hidden.

    ..note::
        This implementation assumes the display layer's visibility attribute
        is never animated.

    Roughly based on: http://ewertb.soundlinker.com/mel/mel.098.php

    :return: Whether the node is visible in the scene
    :rtype: bool
    """

    if frames is None:
        frames = []

    check_frames = not frames

    # Only existing objects can be visible
    if not cmds.objExists(node):
        return False

    # Only dagNodes can be visible
    if not cmds.objectType(node, isAType='dagNode'):
        return False

    node_attr_visibility = '{0}.visibility'.format(node)
    node_attr_intermediate_object = '{0}.intermediateObject'.format(node)

    # Display Layer
    if display_layer:
        # The display layer sets the overrideEnabled and
        # overrideVisibility on the node to toggle visibility
        if cmds.attributeQuery('overrideEnabled', node=node, exists=True):
            if cmds.getAttr('{0}.overrideEnabled'.format(node)) and \
               cmds.getAttr('{0}.overrideVisibility'.format(node)):
                return False

    # Visibility
    iter_visibility = False
    if visibility:
        if is_driven(node_attr_visibility):
            iter_visibility = True
        elif not cmds.getAttr(node_attr_visibility):
            return False

    # Intermediate Object (only for shapes)
    iter_intermediate_object = False
    if intermediate_object and cmds.objectType(node, isAType='shape'):
        if is_driven(node_attr_intermediate_object):
            iter_intermediate_object = True
        elif cmds.getAttr(node_attr_intermediate_object):
            return False

    # If we check at times it'll become much trickier, since we need to check
    # whether the node is visible at least once at the given frames or its
    # hidden in all (or any of its parents)!
    iter_time = any([iter_visibility, iter_intermediate_object])
    if check_frames and iter_time:
        for frame in frames:
            # Whenever it's considered not visible we continue

            if iter_visibility and \
               not cmds.getAttr(node_attr_visibility, t=frame):
                continue

            if iter_intermediate_object and \
               cmds.getAttr(node_attr_intermediate_object, t=frame):
                continue

            # If we get to here the node is visible at the given frame so we
            # skip looking further
            break
        else:
            # When the loop was never broken the object was never 'visible'
            return False

    if parent:
        parent_node = cmds.listRelatives(node,
                                         parent=True,
                                         fullPath=True)
        if parent_node:
            parent_node = parent_node[0]
            if not is_visible(parent_node,
                              display_layer=display_layer,
                              intermediate_object=False,
                              parent=parent,
                              visibility=visibility,
                              frames=frames):
                return False

    return True