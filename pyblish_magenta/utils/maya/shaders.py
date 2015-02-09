from maya import cmds
import itertools


def get_shading_engines(nodes):
    """ Return the related shadingEngines for given node shapes.

    We can get the shadingEngine by doing:
        - maya.cmds.listSets(object=shape, t=1) # t=1 will filter to render sets only
        - maya.cmds.listConnections(shape, type='shadingEngine')

    Invoking a command many times in Maya can often result in a big performance hit.
    The `listSets` is per object whereas listConnections can run on a full list of nodes.
    Yet `listConnections` returns the same shadingEngine multiple times (a lot; especially with face assignments!).
    In practice I've found listSets to be the winner in both speed and ease of use.

    .. note:: I've seen some issues with listSets and namespaces, like not giving the full name with namespace.
              Need to do some more investigation to that.
    """
    shapes = cmds.ls(nodes, dag=1, lf=1, o=1, s=1)
    if shapes:
        sg = set()
        for shape in shapes:
            render_sets = cmds.listSets(object=shape, t=1, extendToShape=False)
            if render_sets:
                for shading_engine in render_sets:
                    sg.add(shading_engine)

        sg = list(sg)
        return sg
    else:
        return []


def get_shader_assignment(shapes):
    shapes = cmds.ls(shapes, dag=1, shapes=1, long=1)
    if not shapes:
        return {}

    shading_engines = get_shading_engines(shapes)

    assignments = {}
    object_lookup = set(shapes)     # set for faster look-up table
    for sg in shading_engines:
        # Since sg_members can also contain components we need to check whether the member (either component or full
        # shape) is related to the shapes we want information about. Because component (eg. face) assignments are listed
        # with the transform name (eg. '|pSphere1.f[141:146]') it's easiest to enforce it towards the full shape
        # names using cmds.ls(o=True)
        sg_members = cmds.sets(sg, q=1)
        sg_members_objects = cmds.ls(sg_members, o=True, long=True)
        if not sg_members:
            continue

        assignments[sg] = [] # initialize with empty list (we could also use defaultdict!)
        for member, member_object in itertools.izip(sg_members, sg_members_objects):
            if member_object in object_lookup:
                assignments[sg].append(member)

    return assignments


def perform_shader_assignment(assignmentDict):
    for shadingGroup, members in assignmentDict.iteritems():
        if members:
            cmds.sets(members, e=True, forceElement=shadingGroup)