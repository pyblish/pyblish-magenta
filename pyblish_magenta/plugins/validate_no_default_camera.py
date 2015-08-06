import pyblish.api
from maya import cmds


class ValidateNoDefaultCameras(pyblish.api.Validator):
    """Ensure no default (startup) cameras are in the instance.

    This might be unnecessary. In the past there were some issues with
    referencing/importing files that contained the start up cameras overriding
    settings when being loaded and sometimes being skipped.
    """

    families = ['animation']
    hosts = ['maya']
    version = (0, 1, 0)
    label = "No Default Cameras"

    def process(self, instance):
        """Process all the cameras in the instance"""
        cameras = cmds.ls(instance, type='camera', long=True)

        invalid = []
        for cam in cameras:
            if cmds.camera(cam, query=True, startupCamera=True):
                invalid.append(cam)

        assert not invalid, "Default cameras found: {0}".format(invalid)