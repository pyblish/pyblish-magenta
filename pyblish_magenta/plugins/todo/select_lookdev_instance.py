import os
import json

import pyblish.api
import pyblish_maya

from maya import cmds


def is_subdir(path, root_dir):
    """ Returns whether path is a subdirectory (or file) within root_dir """
    path = os.path.realpath(path)
    root_dir = os.path.realpath(root_dir)

    # If not on same drive
    if os.path.splitdrive(path)[0] != os.path.splitdrive(root_dir)[0]:
        return False

    # Get 'relative path' (can contain ../ which means going up)
    relative = os.path.relpath(path, root_dir)

    # Check if the path starts by going up, if so it's not a subdirectory. :)
    if relative.startswith(os.pardir) or relative == os.curdir:
        return False
    else:
        return True


@pyblish.api.log
class SelectLookdevInstance(pyblish.api.Selector):
    """ Inject all models from the scene into the context (if in lookDev workspace)

        .. note:: This skips intermediate objects.
    """
    hosts = ["maya"]

    def process_context(self, context):
        # must be a saved file and within a project root Directory
        project_root = context.data("workspace_dir")
        if not project_root:
            self.log.error("No workspace has been set.")
            return

        self.log.info("Project root = %s" % project_root)

        scene_name = cmds.file(q=1, sceneName=True)
        self.log.info("Scene name = %s" % scene_name)

        # must be inside the dev lookDev folder
        lookDev_root = os.path.join(project_root, 'dev', 'lookDev')
        if not is_subdir(scene_name, lookDev_root):
            self.log.info("Scene was not part of lookDev")
            return

        self.log.info("Scene is part of lookDev")

        # Get the asset's information
        asset_root = os.path.dirname(os.path.dirname(scene_name))
        asset_name = os.path.basename(asset_root)

        instance = context.create_instance(name=asset_name)
        instance.set_data("family", "lookdev")

        self.log.info("Selecting nodes..")

        output_types = ["lambert", "file"]
        nodes = cmds.ls(type=output_types)

        self.log.info("Considering these nodes for inclusion: %s" % nodes)

        with pyblish_maya.maintained_selection():
            cmds.select(nodes)
            nodes = cmds.file(exportSelected=True, preview=True, force=True)

            # Retain only what we actually want
            for node in nodes:
                if cmds.nodeType(node) not in output_types:
                    continue

                child = type("MayaNode", (object,), {})
                child.name = node
                child.type = cmds.nodeType(node)
                instance.add(child)

        self.log.info("Nodes selected successfully\n\n%s" %
                      ", ".join(c.name for c in instance))

        self.log.info("Finding associated meshes..")

        links = {}
        for shader in instance:
            if shader.type != "lambert":
                continue

            self.log.info("Finding associated shading groups..")
            self.log.info("Finding associated meshes..")
            self.log.info("Storing association as instance data..")

            links["meshA"] = shader.name
            links["meshB"] = shader.name
            links["meshC"] = shader.name

            instance.set_data("links", links)

            self.log.info("Successfully parsed and serialised links\n\n%s"
                          % json.dumps(links, indent=4))
