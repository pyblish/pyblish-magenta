import pyblish.api
import os
import maya.cmds as mc
import pyblish_magenta.utils.maya.context as maya_context
import pyblish_magenta.utils.lib.context as lib_context


class MayaExporter(object):
    @staticmethod
    def export(path, nodes, preserveReferences=True, constructionHistory=True, expressions=True, channels=True,
               constraints=True, displayLayers=True, renderLayers=True, objectSets=True, shader=True,
               createFolder=True, includeChildren=True, typ='mayaAscii', verbose=False):
        """ An expanded Maya export function that also allows to temporarily disconnect shaders, displayLayers,
            renderLayers and objectSets so they will get skipped for exporting.
        """

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            if createFolder:
                os.makedirs(directory)
            else:
                raise RuntimeError("Output directory does not exist: {0}".format(directory))

        contexts = [maya_context.PreserveSelection()]

        if not shader:
            # To exclude shaders from exporting we will temporarily assign the default shader as opposed to setting
            # the shader parameter to False on the `maya.cmds.file` command. This is because the maya command creates
            # a file that comes up with only a wireframe (not even scene's default shader assigned) if shader=False
            # on export.
            shapes = mc.ls(nodes, shapes=True, long=True)
            temp_shader_context = maya_context.TemporaryShaders(shapes, 'initialShadingGroup')
            contexts.append(temp_shader_context)

        if not displayLayers:
            # TODO: Test disabling displayLayers
            contexts.append(maya_context.TemporaryDisplayLayer(nodes, 'defaultLayer'))

        if not renderLayers:
            # TODO: Implement disabling renderLayers
            raise NotImplementedError("Disabling renderLayers for export is not implemented yet.")

        if not objectSets:
            # TODO: Implement disabling objectSets
            raise NotImplementedError("Disabling objectSets for export is not implemented yet.")

        if not includeChildren:
            # TODO: Implement disabling includeChildren
            raise NotImplementedError("Disabling includeChildren for export is not implemented yet.")

        with lib_context.ExitStack() as stack:
            for context in contexts:
                stack.enter_context(contexts)

            mc.select(nodes, r=1)
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

        path = os.path.join(workspace_root, 'published', filename)

        # We want to extract without any history and/or shaders.
        # We can disable shaders with the file export; though upon import the mesh won't
        # even receive the default lambert and gets imported without any default shader.
        # This is an annoying inconvenience; so instead we apply the default lambert1
        # before export and re-apply the current shader after export
        export_nodes = mc.ls(instance, long=True)
        export_shapes = mc.ls(export_nodes, long=True, shapes=True)

        output = MayaExporter.export(export_nodes, preserveReferences=False, constructionHistory=False,
                                     expressions=False, channels=False, constraints=False, shader=False,
                                     displayLayers=False, renderLayers=False, objectSets=False)

        self.log.info("Extracted instance '{0}' to: {1}".format(instance.name, path))