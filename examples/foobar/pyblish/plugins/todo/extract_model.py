import pyblish.api
import os
import maya.cmds as mc
import pyblish_magenta.utils.maya.context as maya_context
import pyblish_magenta.utils.lib.context as lib_context


class MayaExporter(object):
    @staticmethod
    def export(path, nodes, preserveReferences=True, constructionHistory=True, expressions=True, channels=True,
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
            # TODO: Test disabling displayLayers
            contexts.append(maya_context.TemporaryDisplayLayer(nodes, 'defaultLayer'))

        # if renderLayers:
        #     # TODO: Implement enabling renderLayers? Worth it? Too buggy anyway?
        #     # Might need workaround for Maya bug for renderLayer overrides by temporarily switching to masterLayer?
        #     # Is that expected behaviour?
        #     raise NotImplementedError("Enabling renderLayers for export is not implemented yet.")

        if objectSets:
            # objectSets are not implicitly exported if not provided as part of the nodes list.
            # Though if you include the objectSet explicitly (as part of the node list) all its members WILL get
            # included in the export.
            # TODO: Implement enabling exprt of connected objectSets (with only implicit members in the list)
            raise NotImplementedError("Enabling objectSets for export is not implemented yet.")

        if not includeChildren:
            # TODO: Test disabling includeChildren
            # Unparent those nodes that are children of the export nodes who are not explicitly included in the export
            # list. This way they will get skipped for the export.
            all_nodes_lookup = set(mc.ls(nodes, long=True))     # ensure long names
            all_children = mc.listRelatives(nodes, children=True, allDescendents=True, fullPath=True)

            exclude_nodes = [node for node in all_children if node not in all_nodes_lookup]
            if exclude_nodes:
                contexts.append(maya_context.TemporaryUnparent(exclude_nodes, preserve_order=True))
        # endregion

        # Perform the export with the chosen contexts and settings
        with lib_context.ExitStack() as stack:
            for context in contexts:
                stack.enter_context(context)

            mc.select(nodes, r=1, noExpand=True)
            return mc.file(path, force=True, options='v={0};'.format(int(verbose)), typ=typ,
                           preserveReferences=preserveReferences,
                           exportSelected=True,
                           constructionHistory=constructionHistory,
                           expressions=expressions,
                           channels=channels,
                           constraints=constraints,
                           shader=True)


@pyblish.api.log
class ExtractModel(pyblish.api.Extractor):
    """
        Exports all nodes
    """
    hosts = ["maya"]
    families = ["model"]

    def process_instance(self, instance):

        filename = "{0}.ma".format(instance.name)
        workspace_root = mc.workspace(q=1, rootDirectory=True)
        publish_directory = os.path.join(workspace_root, 'published')

        path = os.path.join(publish_directory, filename)
        export_nodes = mc.ls(instance, long=True)

        output = MayaExporter.export(export_nodes, preserveReferences=False, constructionHistory=False,
                                     expressions=False, channels=False, constraints=False, shader=False,
                                     displayLayers=False, objectSets=False)

        self.log.info("Extracted instance '{0}' to: {1}".format(instance.name, path))