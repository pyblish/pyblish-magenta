import os
from collections import defaultdict
import logging
import contextlib

import maya.cmds as mc

import pyblish_magenta.utils.maya.context as maya_context

log = logging.getLogger(__name__)


def get_all_parents(long_name):
    parents = long_name.split("|")[1:-1]
    return ['|{0}'.format('|'.join(parents[0:i + 1])) for i in
            xrange(len(parents))]


def export(path='',
           # collection/data to export
           nodes=None,
           constructionHistory=True,
           expressions=True,
           channels=True,
           constraints=True,
           displayLayers=True,
           objectSets=False,
           shader=True,
           includeChildren=True,
           # output
           createFolder=True,
           preserveReferences=True,
           smoothPreview=None,
           typ='mayaAscii',
           # settings
           verbose=False,
           preview=False):
    """ A wrapper around `maya.cmds.file` to perform exporting a set of nodes
    more explicitly instead of including implicit connections.

    This allows to skip exporting shaders, displayLayers, renderLayers,
    objectSets and so forth that a node belongs to.

    How it works:
        Before exporting we build a list of Python context managers that will
        perform a change in the Maya scene for the duration of the export
        and then revert back to its previous state. It's assumed that the
        Context managers are implemented in such a way that they don't leave
        any trace inside the scene. (The artist finds his/her work scene
        unchanged after export).

    .. note::
        renderLayers are not implicitly exported with nodes out of Maya unless
        explicitly included in the nodes that must be exported. If you
        export nodes whilst being in non-default renderLayers any
        renderLayer overrides will be assigned to the nodes as if it's the
        default value. On the other hand when exporting from default render
        layer (masterLayer?) it seems to work upon import, until you switch
        to the layer with overrides and back to the masterLayer. Then the
        node will not revert to its non-overridden value in the imported scene.
    """
    # Ensure long names
    if nodes is None:
        nodes = mc.ls(sl=True, long=True)
    else:
        nodes = mc.ls(nodes, long=True)

    if not nodes:
        raise RuntimeError("Nothing to export")

    # We always include the hierarchy above nodes.
    # Get all parent nodes (by long name)
    export_nodes = set()
    export_nodes.update(nodes)
    for node in nodes:
        export_nodes.update(get_all_parents(node))
    nodes = list(export_nodes)

    # If we're doing a real live export ensure `path` is valid for output
    if not preview:
        if not path:
            raise RuntimeError(
                "A path must be provided if not in preview mode.")

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            if createFolder:
                os.makedirs(directory)
            else:
                raise RuntimeError(
                    "Output directory does not exist: {0}".format(
                        directory))

    # region build contexts
    contexts = list()

    # Always preserve selection
    contexts.append(maya_context.PreserveSelection())

    if not shader:
        # To exclude shaders from exporting we temporarily assign the default
        # shader as opposed to setting `shader=False` on `maya.cmds.file`.
        # Otherwise it creates a file that imports solely as wireframe and
        # has no default shader assigned.
        shapes = mc.ls(nodes, shapes=True, long=True, dag=True, leaf=True)

        ctx = maya_context.TemporaryShaders(shapes, 'initialShadingGroup')
        contexts.append(ctx)

    if not displayLayers:
        ctx = maya_context.TemporaryDisplayLayer(nodes, 'defaultLayer')
        contexts.append(ctx)

    # TODO: Implement *include renderLayers* (or is it too buggy?)
    # Might need workaround for Maya bug for renderLayer overrides by
    # temporarily switching to masterLayer?
    # if renderLayers:
    # raise NotImplementedError

    # TODO: Implement objectSets export without expanding (expandObjectSets)
    # TODO: Test whether `objectSets=True` is production-ready
    if objectSets:
        # objectSets are not implicitly exported if not provided as part of the
        # nodes list. Though if you include the objectSet explicitly (as
        # part of the node list) all its members WILL get included in the
        # export.

        # Get the related object_sets and the explicit nodes that are
        # contained within them
        object_sets_relationships = defaultdict(set)
        for node in nodes:
            object_sets = mc.ls(mc.listSets(object=node),
                                exactType='objectSet')
            for object_set in object_sets:
                object_sets_relationships[object_set].add(node)

        # Now we have our connected `implicit_object_sets`
        implicit_object_sets = object_sets_relationships.keys()

        # If one of the `implicit_object_sets` is already in the explicit
        # `nodes` to export than we don't need to filter that objectSet.
        # Then we will always allow Maya to take the full set of nodes.
        for object_set in implicit_object_sets:
            if object_set in nodes:
                del object_sets_relationships[object_set]

        for object_set, object_set_nodes in \
                object_sets_relationships.iteritems():
            ctx = maya_context.TemporaryObjectSetSolo(object_set=object_set,
                                                      nodes=object_set_nodes)
            contexts.append(ctx)

    if not includeChildren:
        # Un-parent nodes that are children of the export nodes who are not
        # explicitly included in the export list. This way they will get
        # skipped for the export.
        all_nodes_lookup = set(mc.ls(nodes, long=True))  # ensure long names
        all_children = mc.listRelatives(nodes,
                                        children=True,
                                        allDescendents=True,
                                        fullPath=True)

        exclude_nodes = [node for node in all_children if
                         node not in all_nodes_lookup]

        if exclude_nodes:
            # We'll have to ensure autokeying is OFF, because otherwise Maya
            # sometimes put keys on an object when it gets unparented.
            autokey_ctx = maya_context.TemporaryAutoKeyframeState(False)
            contexts.append(autokey_ctx)

            ctx = maya_context.TemporaryUnparent(exclude_nodes,
                                                 preserve_order=True,
                                                 relative=True)
            contexts.append(ctx)

    if smoothPreview is not None:
        state = bool(smoothPreview)
        ctx = maya_context.TemporarySmoothPreviewSimple(nodes, state)
        contexts.append(ctx)
    # endregion

    if not nodes:
        raise RuntimeError("Nothing to export")

    # Perform the export with the chosen contexts and settings
    with contextlib.nested(*contexts):

        mc.select(nodes, r=1, noExpand=True)
        output = mc.file(path, force=True,
                         options='v={0};'.format(int(verbose)), typ=typ,
                         preserveReferences=preserveReferences,
                         exportSelected=True,
                         constructionHistory=constructionHistory,
                         expressions=expressions,
                         channels=channels,
                         constraints=constraints,
                         shader=True,
                         preview=preview)

        if verbose:
            log.debug("Exported '%s' file to: %s", typ, output)

        return output
