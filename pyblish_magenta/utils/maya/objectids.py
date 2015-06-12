""" WIP; need to move more stuff over and clean it up """
import logging

import maya.cmds as mc
import maya.api.OpenMaya as om2


log = logging.getLogger(__name__)




def __list_id_keys():
    """
        Returns the names of the object id attributes that actually matter for identification.
        This is not necessarily all attributes that were created by the createObjectId function.
    """
    return ['name',
            'parent_hierarchy',
            'object_id']


def define_asset_id(path=None):
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


def define_node_id(node, asset_id=None):
    """
        Define the asset information for the given node. (not based on stored attributes, but as new unique identifier)
        :return: Scene ID
        :rtype: dict
    """
    if asset_id is None:
        asset_id = define_asset_id()

    # Make copy of scene_id
    id = {}
    id.update(asset_id)

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

    asset_id = define_asset_id()

    id = {}
    for node in nodes:
        node_id = define_node_id(node, asset_id=asset_id)
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


def assign(node, id=None, allow_update=True, verbose=True):
    assert isinstance(id, dict)
    for key, value in id.iteritems():

        # Remap key to correct attr_name
        attr_name = ATTRIBUTES.get(key, None)
        if attr_name is None:
            if verbose:
                log.warning("Key is not in attributes map: '{0}'. Node: {1}".format(key, node))
            attr_name = key

        node_attr = '{0}.{1]'.format(node, attr_name)
        attr_exists = mc.objExists(node_attr)

        # create attribute if not exists
        if not attr_exists:
            mc.addAttr(node, dt='string', ln=attr_name, keyable=True)

        # set the value (update only if allow_update)
        if not attr_exists or allow_update:
            mc.setAttr(node_attr, value, type='string')


def list_similar(nodes=None, **kwargs):
    """
        List all nodes in the scene with similar object ids.
    """
    raise NotImplementedError() # TODO: Move and clean implementation from CB