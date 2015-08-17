import maya.api.OpenMaya as om
import maya.cmds as cmds


def lsattr(attr, value=None):
    """Return nodes matching `key` and `value`

    Arguments:
        attr (str): Name of Maya attribute
        value (object, optional): Value of attribute. If none
            is provided, return all nodes with this attribute.

    Example:
        >> lsattr("id", "myId")
        ["myNode"]
        >> lsattr("id")
        ["myNode", "myOtherNode"]

    """

    if value is None:
        return cmds.ls("*.%s" % attr)
    return lsattrs({attr: value})


def lsattrs(attrs):
    """Return nodes with the given attribute(s).

    Arguments:
        attrs (dict): Name and value pairs of expected matches

    Example:
        >> lsattr("age")  # Return nodes with attribute `age`
        >> lsattr({"age": 5})  # Return nodes with an `age` of 5
        >> # Return nodes with both `age` and `color` of 5 and blue
        >> lsattr({"age": 5, "color": "blue"})

    Returns a list.

    """

    dep_fn = om.MFnDependencyNode()
    dag_fn = om.MFnDagNode()

    first_attr = attrs.iterkeys().next()

    try:
        selection_list = om.MGlobal.getSelectionListByName(
            "*.{0}".format(first_attr))
    except RuntimeError:
        return []

    namespaces = cmds.namespaceInfo(":", recurse=True, listOnlyNamespaces=True)
    max_namespace_levels = max(namespaces, key=lambda n: n.count(":"))

    # NOTE(marcus): To Roy, this is an interesting way of handling it :)
    count = 0
    for x in range(max_namespace_levels):
        try:
            selection_list.add("{0}*.{1}".format("*:"*(x+1), first_attr))
        except RuntimeError:
            if count >= max_namespace_levels:
                raise
            else:
                pass

    if selection_list.length() < 1:
        return []

    matches = set()
    for i in range(selection_list.length()):
        node = selection_list.getDependNode(i)
        if node.hasFn(om.MFn.kDagNode):
            fn_node = dag_fn.setObject(node)
            full_path_names = [path.fullPathName()
                               for path in fn_node.getAllPaths()]
        else:
            fn_node = dep_fn.setObject(node)
            full_path_names = [fn_node.name()]

        for attr in attrs:
            try:
                plug = fn_node.findPlug(attr, True)
                if plug.asString() != attrs[attr]:
                    break
            except RuntimeError:
                break
        else:
            matches.update(full_path_names)

    return list(matches)
