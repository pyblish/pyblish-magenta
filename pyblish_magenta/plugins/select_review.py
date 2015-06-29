import pyblish.api

import maya.cmds as cmds
import pyblish_magenta.schema


@pyblish.api.log
class SelectCameras(pyblish.api.Selector):
    hosts = ['maya']
    label = 'Select via Object Set'

    def process(self, context):
        for camera_shape in cmds.ls("*_CAPShape",
                              objectsOnly=True,
                              type='camera',
                              long=True,
                              recursive=True):  # Include namespace

            camera = cmds.listRelatives(camera_shape, parent=True)[0]
            name = cmds.ls(camera, long=False)[0].rsplit("_CAP", 1)[0].title()  # Use short name
            scene_name = cmds.file(q=1, sceneName=True)
            schema = pyblish_magenta.schema.load()

            instance = context.create_instance(name=name, family="review")
            instance.add(camera)

            # Set Pipeline data
            data = schema.get("model.dev").parse(scene_name)
            instance.set_data("root", data['root'])
            instance.set_data("source_file", scene_name)
            instance.set_data("asset", data['asset'])
            instance.set_data("container", data['container'])

            self.log.info("Found: {0}".format(camera))

            attrs = cmds.listAttr(camera, userDefined=True) or list()
            for attr in attrs:
                if attr == 'parent':
                    # Instance has a parent instance
                    parent_instance = cmds.listConnections(
                        camera + ".parent",
                        destination=False,
                        source=True)
                    instance.set_data('parent', parent_instance)

                try:
                    value = cmds.getAttr(camera + "." + attr)
                except:
                    continue

                instance.set_data(attr, value=value)
