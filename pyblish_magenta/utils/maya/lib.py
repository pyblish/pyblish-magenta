import os
import json

import maya.api.OpenMaya as om
import maya.cmds as cmds

import pyblish_magenta.schema


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
    selection_list = om.MSelectionList()

    first_attr = attrs.iterkeys().next()

    try:
        selection_list.add("*.{0}".format(first_attr), 
                           searchChildNamespaces=True)
    except RuntimeError, e:
        if str(e).endswith("Object does not exist"):
            return []

    # NOTE(Roy): To Marcus, this should be redundant because of above captured error  
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


def lookdev_link():
    schema = pyblish_magenta.schema.load()
    origins = dict()
    for reference in cmds.ls(type="reference"):
        if reference in ("sharedReferenceNode",):
            continue

        filename = cmds.referenceQuery(reference, filename=True)

        # Determine version of reference
        # NOTE(marcus): Will need to determine whether we're in a shot, or asset
        data = schema["shot.full"].parse(filename)
        version = data["version"]
        
        # Reduce filename to the /publish directory
        template = schema["shot.publish"]
        data = template.parse(filename)
        root = template.format(data)

        versiondir = os.path.join(root, version)
        origindir = os.path.join(versiondir, "metadata", "origin").replace("/", "\\")
        if not os.path.exists(origindir):
            continue  # no origin

        originfile = os.path.join(origindir, os.listdir(origindir)[0])

        if not originfile in origins:
            with open(originfile) as f:
                origins[originfile] = json.load(f)

        origin = origins[originfile]

        if not origin["references"]:
            continue  # no references, no match

        reference = origin["references"][0]
        template = schema["asset.publish"]
        data = {
            "asset": reference["item"],
            "root": data["root"],
            "task": "lookdev"
        }
        assetdir = template.format(data)
        
        # NOTE(marcus): Need more robust version comparison
        version = sorted(os.listdir(assetdir))[-1]
        instancedir = os.path.join(assetdir, version, "lookdev", reference["item"])

        # NOTE(marcus): Will need more robust versions of these
        shaderfile = next(os.path.join(instancedir, f) for f in os.listdir(instancedir) if f.endswith(".ma"))
        linksfile = next(os.path.join(instancedir, f) for f in os.listdir(instancedir) if f.endswith(".json"))
        
        # Load shaders
        # NOTE(marcus): We'll need this to be separate, at least functionally
        namespace = "%s_shaders_" % reference["item"]
        if namespace not in cmds.namespaceInfo(
                ":", recurse=True, listOnlyNamespaces=True):
            cmds.file(shaderfile, reference=True, namespace=namespace)

        with open(linksfile) as f:
            payload = json.load(f)

        for shading_group_data in payload:
            try:
                shading_group_node = lsattrs({"uuid": shading_group_data["uuid"]})[0]
            except:
                # This would be a bug
                print("%s wasn't in the look dev scene" % shading_group_data["name"])
                continue

            for member_data in shading_group_data["members"]:
                try:
                    member_node = lsattrs({"uuid": member_data["uuid"]})[0]
                except:
                    # This would be inconsistent
                    print("%s wasn't in the lighting scene" % shading_group_data["name"])
                    continue

                print("Adding \"%s\" to \"%s\"" % (member_node, shading_group_node))
                cmds.sets(member_node, forceElement=shading_group_node)
