import pyblish.api
import maya.cmds as cmds

from pyblish_magenta.utils.path import is_subdir


class ValidateSceneSetWorkspace(pyblish.api.Validator):
    """Validate the scene is inside the currently set Maya workspace"""

    families = ['model']
    hosts = ['maya']
    category = 'scene'
    version = (0, 1, 0)
    label = 'Maya Workspace Set'

    def process(self, context):
        scene_name = cmds.file(q=1, sceneName=True)
        root_dir = cmds.workspace(q=1, rootDirectory=True)

        if not is_subdir(scene_name, root_dir):
            raise RuntimeError("Maya workspace is not set correctly.")
