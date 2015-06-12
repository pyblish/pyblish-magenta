# stdlib
import os
from collections import defaultdict
import logging
import contextlib

# maya & pyblish lib
import maya.cmds as mc

# local lib
import pyblish_magenta.utils.maya.context as maya_context


def get_all_parents(longName):
    parents = longName.split("|")[1:-1]
    return ['|{0}'.format('|'.join(parents[0:i+1])) for i in xrange(len(parents))]


class MayaExporter(object):
    log = logging.getLogger(__name__ + '.MayaExporter')

    @staticmethod
    def export(path, nodes=None, preserveReferences=True, constructionHistory=True, expressions=True, channels=True,
               constraints=True, displayLayers=True, objectSets=False, shader=True,
               createFolder=True, includeChildren=True, typ='mayaAscii', verbose=False):
        """ An expanded Maya export function that also allows to temporarily disconnect shaders, displayLayers,
            renderLayers and objectSets so they will get skipped for exporting.

            Before exporting we build a stack of Context managers that will perform a change in the Maya scene for the
            duration of the export and then revert back to its previous state. It's assumed that the Context managers
            are implemented in such a way that they don't leave any trace inside the scene. (The artist finds his/her
            work scene unchanged after export).

            .. note:: renderLayers are not implicitly exported with nodes out of Maya unless explicitly included
                      in the nodes that must be exported. If you export nodes whilst being in non-default renderLayers
                      any renderLayer overrides will be assigned to the nodes as if it's the default value. On the other
                      hand when exporting from default render layer (masterLayer?) it seems to work upon import, until
                      you switch to the layer with overrides and back to the masterLayer. Then the node will not revert
                      to its non-overridden value in the imported scene.
        """
        # TODO: Allow explicit objectSets to be exported without its members by `expandObjectSets=False` parameter

        # Ensure long names
        if nodes is None:
            nodes = mc.ls(sl=True, long=True)
        else:
            nodes = mc.ls(nodes, long=True)

        # Get all parent nodes (by long name)
        export_nodes = set()
        export_nodes.update(nodes)
        for node in nodes:
            export_nodes.update(get_all_parents(node))
        nodes = list(export_nodes)

        if not nodes:
            raise RuntimeError("Nothing to export")

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            if createFolder:
                os.makedirs(directory)
            else:
                raise RuntimeError("Output directory does not exist: {0}".format(directory))

        # region build contexts
        contexts = [maya_context.PreserveSelection()]

        if not shader:
            # To exclude shaders from exporting we will temporarily assign the default shader as opposed to setting
            # the shader parameter to False on the `maya.cmds.file` command. This is because the maya command creates
            # a file that comes up with only a wireframe (not even scene's default shader assigned) if shader=False
            # on export. This is an annoying inconvenience; so instead we apply the default lambert1  before export and
            # re-apply the current shader after export
            shapes = mc.ls(nodes, shapes=True, long=True)
            contexts.append(maya_context.TemporaryShaders(shapes, 'initialShadingGroup'))

        if not displayLayers:
            contexts.append(maya_context.TemporaryDisplayLayer(nodes, 'defaultLayer'))

        # if renderLayers:
        #     # TODO: Implement enabling renderLayers? Worth it? Too buggy anyway?
        #     # Might need workaround for Maya bug for renderLayer overrides by temporarily switching to masterLayer?
        #     # Is that expected behaviour?
        #     raise NotImplementedError("Enabling renderLayers for export is not implemented yet.")

        if objectSets:
            # TODO: Test current implementation: enable export connected objectSets (with only implicit members in list)
            # TODO: Add preservation of nested objectSets (IF any of exported nodes is contained explicitly or implicitly)
            # objectSets are not implicitly exported if not provided as part of the nodes list.
            # Though if you include the objectSet explicitly (as part of the node list) all its members WILL get
            # included in the export.

            # Get the related object_sets and the explicit nodes that are contained within them
            object_sets_relationships = defaultdict(set)
            for node in nodes:
                object_sets = mc.ls(mc.listSets(object=node), exactType='objectSet')
                for object_set in object_sets:
                    object_sets_relationships[object_set].add(node)

            # Now we have our connected `implicit_object_sets`
            implicit_object_sets = object_sets_relationships.keys()

            # If one of the `implicit_object_sets` is already in the explicit `nodes` to export than we don't need to
            # filter that objectSet. Then we will always allow Maya to take the full set of nodes.
            for object_set in implicit_object_sets:
                if object_set in nodes:
                    del object_sets_relationships[object_set]

            for object_set, object_set_nodes in object_sets_relationships.iteritems():
                contexts.append(maya_context.TemporaryObjectSetSolo(object_set=object_set, nodes=object_set_nodes))

        if not includeChildren:
            # Unparent those nodes that are children of the export nodes who are not explicitly included in the export
            # list. This way they will get skipped for the export.
            all_nodes_lookup = set(mc.ls(nodes, long=True))     # ensure long names
            all_children = mc.listRelatives(nodes, children=True, allDescendents=True, fullPath=True)

            exclude_nodes = [node for node in all_children if node not in all_nodes_lookup]
            if exclude_nodes:
                # We'll have to ensure autokeying is OFF, because otherwise Maya sometimes put keys on an object
                # when it gets unparented.
                contexts.append(maya_context.TemporaryAutoKeyframeState(False))
                contexts.append(maya_context.TemporaryUnparent(exclude_nodes, preserve_order=True, relative=True))
        # endregion

        # Perform the export with the chosen contexts and settings
        output = None
        with contextlib.nested(*contexts):

            if not nodes:
                raise RuntimeError("Nothing to export")

            mc.select(nodes, r=1, noExpand=True)
            output = mc.file(path, force=True, options='v={0};'.format(int(verbose)), typ=typ,
                           preserveReferences=preserveReferences,
                           exportSelected=True,
                           constructionHistory=constructionHistory,
                           expressions=expressions,
                           channels=channels,
                           constraints=constraints,
                           shader=True)

            if verbose:
                MayaExporter.log.debug("Exported '%s' file to: %s", typ, output)

        return output
