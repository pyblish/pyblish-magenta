""" WIP; need to move more stuff over and clean it up """

import maya.cmds as mc
import maya.api.OpenMaya as om2


ATTRIBUTES = {'name': 'cbAssetName',
              'parent_hierarchy' :'cbAssetParentHierarchy',
              'object_id': 'cbAssetObjectId',
              'source': 'cbFullPath',
              'project_root': 'cbFullPath',
              'workspace': 'cbWorkspace',
              'shader_variation': 'cbShaderVariation'}
# Reverse mapping
ATTRIBUTES_REV = dict((y, x) for x, y in ATTRIBUTES.items())


def __list_id_keys():
    """
        Returns the names of the object id attributes that actually matter for identification.
        This is not necessarily all attributes that were created by the createObjectId function.
    """
    return ['name',
            'parent_hierarchy',
            'object_id']


def define_scene_id(path=None):
    """
        Define the asset information for the current scene
        :return: Scene ID
        :rtype: dict
    """
    # TODO: Move and clean implementation from CB
    raise NotImplementedError()

    if path is None:
        path = mc.file(q=1, sceneName=True)

    id = {}
    id['name'] = 'name'
    id['parent_hierarchy'] = 'parent_hierarchy'
    return id


def define_node_id(node, scene_id=None):
    """
        Define the asset information for the given node. (not based on stored attributes, but as new unique identifier)
        :return: Scene ID
        :rtype: dict
    """
    if scene_id is None:
        scene_id = define_scene_id()

    # Make copy of scene_id
    id = {}
    id.update(scene_id)

    # Add object id data
    id[ATTRIBUTES['object_id']] = mc.ls(node, long=True)[0]   # long name
    return id


def create(nodes, allow_update=True):
    """ Add (and update) the object ids for nodes.
    :param nodes:
    :param skip_update:
    :return: Generated object ids
    """

    result = []

    if not isinstance(nodes, (tuple, list)):
        nodes = [nodes]

    scene_id = define_scene_id()

    id = {}
    for node in nodes:
        node_id = define_node_id(node, scene_id=scene_id)
        assign(node, node_id, allow_update=allow_update)
        result.append(node_id)

    return result


def get(node, useApi2=True):
    """
        Gets the object id information from the node

        useApi2 assumes that the value to get are always string values. (faster)
    """
    attributes = dict([(x, None) for x in __list_id_keys()])
    if useApi2:
        selList = om2.MGlobal.getSelectionListByName(node)
        fnNode = om2.MFnDependencyNode(selList.getDependNode(0))
        for key in attributes.iterkeys():
            attr_name = ATTRIBUTES[key]
            try:
                attributes[key] = fnNode.findPlug(attr_name, True).asString()
            except RuntimeError:
                continue
    else:
        for key in attributes.iterkeys():
            attr_name = ATTRIBUTES[key]
            nodeAttr = "{0}.{1}".format(node, attr_name)
            if mc.objExists(nodeAttr):
                attributes[key] = mc.getAttr(nodeAttr)

    return attributes


def remove(nodes):
    """
        Removes objectIds from nodes if any
    """
    for node in nodes:
        for key in __list_id_keys():
            attr_name = ATTRIBUTES[key]
            node_attr = '{0}.{1]'.format(node, attr_name)
            if mc.objExists(node_attr):
                mc.deleteAttr(node_attr)


def assign(node, id=None, allow_update=True):

    for key, value in id.iteritems():
        attr_name = ATTRIBUTES[key]
        if not


    # TODO: Move and clean implementation from CB
    raise NotImplementedError()


def list_similar(nodes=None, **kwargs):
    """
        List all nodes in the scene with similar object ids.
    """
    # TODO: Move and clean implementation from CB
    raise NotImplementedError()