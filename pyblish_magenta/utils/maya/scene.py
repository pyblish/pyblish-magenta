# stdlib
from collections import OrderedDict, Counter
from itertools import izip, repeat

# maya lib
from maya import cmds


def getDagOrder(filter_shapes=True):
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
    dagNodes = cmds.ls(dag=True, long=True)

    # Turn the node list into an ordered dictionary (with None as temp value)
    dagNodes = OrderedDict(izip(dagNodes, repeat(None)))

    # Remove the shapes from the dictionary
    if filter_shapes:
        for shape in cmds.ls(shapes=True, long=True):
            # We use `dict.pop(index, None)` instead `del dict[index]` as the key might not exist.
            dagNodes.pop(shape, None)

    # For each calculate amount of parents
    # Since everything listed so far is in order we count it ourselves
    hierarchyCounter = Counter()
    for node in dagNodes:
        parent = node.rpartition("|")[0]
        dagNodes[node] = hierarchyCounter[parent]
        hierarchyCounter[parent] += 1

    return dagNodes