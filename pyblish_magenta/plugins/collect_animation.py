import os
import pyblish.api
import pyblish_maya

from pyblish_magenta.utils.maya.scene import is_visible


@pyblish.api.log
class CollectAnimation(pyblish.api.Collector):
    """Inject meshes and cameras from the scene into the context"""

    def process(self, context):
        from maya import cmds

        if not os.environ["TASK"] == "animation":
            return self.log.info("No animation found")

        name = os.environ["ITEM"]

        # Get the root transform
        self.log.info("Animation found: %s" % name)

        start_frame = 1
        end_frame = 10
        frames = range(start_frame, end_frame)

        # Collect visible meshes
        meshes = cmds.ls(noIntermediate=True,
                         exactType="mesh",
                         long=True,
                         dag=True)

        visible_meshes = list()
        for mesh in meshes:
            if is_visible(mesh,
                          display_layer=False,
                          intermediate_object=False,
                          visibility=True,
                          parent=True,
                          frames=frames):
                visible_meshes.append(mesh)

        # Collect non-default cameras
        cameras = cmds.ls(exactType='camera',
                          long=True,
                          dag=True)

        non_default_cameras = list()
        for camera in cameras:
            if not cmds.camera(camera, query=True, startupCamera=True):
                non_default_cameras.append(camera)

        nodes = visible_meshes + non_default_cameras
        assert nodes, "Animation does not have any nodes"

        instance = context.create_instance(name=name, family="animation")
        instance[:] = nodes

        self.log.info("Successfully collected %s" % name)
