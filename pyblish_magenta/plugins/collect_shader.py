import os
import pyblish.api


class CollectShaders(pyblish.api.Collector):
    label = "Collect Shaders"
    hosts = ["maya"]

    def process(self, context):
        from maya import cmds

        self.log.info("Looking for shader associations..")
        if not cmds.objExists("assigned_SET"):
            return self.log.info("Nothing found")

        all_shaders = set()
        links = dict()
        for mesh in cmds.sets("assigned_SET", query=True):
            mesh = cmds.ls(mesh, long=True, absoluteName=True)[0]

            # Discover related shader(s)
            shader = cmds.listConnections(
                cmds.listHistory(mesh, f=True), type='shadingDependNode')[0]

            # Store links between mesh->shader(s)
            if shader not in links:
                links[shader] = list()

            links[shader].append(mesh)

            # Store reference of shaders for extraction
            all_shaders.add(shader)

        item = os.environ["ITEM"]
        instance = context.create_instance(item, family="lookdev")

        self.log.info("Gathering links: %s" % links)
        instance.set_data("links", links)

        self.log.info("Collecting shaders: %s" % all_shaders)
        instance[:] = cmds.ls(list(all_shaders), absoluteName=True, long=True)

        self.log.info("Found %s" % instance)
