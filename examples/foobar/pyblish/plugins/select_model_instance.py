from maya import cmds
import pyblish.api
import os


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


class SelectModelInstance(pyblish.api.Selector):
    hosts = ["maya"]

    def process_context(self, context):

        project_root = cmds.workspace(q=1, rootDirectory=True)
        scene_name = cmds.file(q=1, sceneName=True)
        if not scene_name:
            # file not saved
            return

        modeling_root = os.path.join(project_root, 'dev', 'modeling')

        # must be a saved file and within a project root Directory
        project_root = cmds.workspace(q=1, rootDirectory=True)
        if not project_root:
            # this never happens?
            return

        scene_name = cmds.file(q=1, sceneName=True)
        if not scene_name:
            # file not saved
            raise RuntimeError("Better to return here, but outside function now :D")

        # must be inside the dev modeling folder
        modeling_root = os.path.join(project_root, 'dev', 'modeling')
        if not is_subdir(scene_name, project_root):
            # not in modeling
            raise RuntimeError("Better to return here, but outside function now :D")

        # assume assetName from two parent directory of 'maya' folder
        assetName = os.path.basename(os.path.dirname(os.path.dirname( scene_name )))

        # get the root transform
        root_transform = cmds.ls('|{assetName}_GRP.id'.format(assetName=assetName), objectsOnly=True, type='transform')
        if not root_transform:
            return
        else:
            root_transform = root_transform[0]


        # get all children shapes (because we're modeling we only care about shapes)
        shapes = cmds.ls(root_transform, dag=True, shapes=True, long=True)
        if not shapes:
            return

        instance = context.create_instance(name=assetName)
        instance.set_data("family", "model")
        for shape in shapes:
            instance.add(shape)

