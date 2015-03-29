import pyblish.api
import maya.cmds as cmds
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


class ValidateSceneSetWorkspace(pyblish.api.Validator):
    """ Validate the scene is inside the currently set Maya workspace """
    families = ['model']
    hosts = ['maya']
    category = 'scene'
    version = (0, 1, 0)

    def process_context(self, context):
        scene_name = cmds.file(q=1, sceneName=True)
        root_dir = cmds.workspace(q=1, rootDirectory=True)

        if not is_subdir(scene_name, root_dir):
            raise RuntimeError("Maya workspace is not set correctly.")

    def repair_context(self, context):
        # TODO: Check if repair_context is an existing feature of Pyblish
        # TODO: Implement looking recursively up in folders towards the closest workspace.mel (if any)
        pass

