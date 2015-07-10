import os
import pyblish.api
import pyblish_maya


@pyblish.api.log
class CollectModel(pyblish.api.Collector):
    """Inject all models from the scene into the context"""

    hosts = ["maya"]

    def process(self, context):
        from maya import cmds

        if not os.environ["TASK"] == "modeling":
            return self.log.info("No model found")

        name = os.environ["ITEM"]

        # Get the root transform
        self.log.info("Model found: %s" % name)
        assembly = "|{name}_GRP".format(name=name)
        root_transform = cmds.ls(assembly,
                                 objectsOnly=True,
                                 type="transform")

        assert root_transform, (
            "Model did not have an appropriate assembly: %s" % assembly)

        self.log.info("Root transform determined to be: %s" % assembly)
        root_transform = root_transform[0]

        shapes = cmds.ls(root_transform,
                         noIntermediate=True,
                         shapes=True,
                         long=True,
                         dag=True)

        assert shapes, "Model did not have any shapes"

        instance = context.create_instance(name=name,
                                           family="model")

        self.log.info("Capturing instance contents: %s" % assembly)
        with pyblish_maya.maintained_selection():
            cmds.select(shapes)
            instance[:] = cmds.file(exportSelected=True,
                                    preview=True,
                                    constructionHistory=True,
                                    force=True)

        self.log.info("Successfully collected %s" % name)
