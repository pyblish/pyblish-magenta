import os
import pyblish.api
import pyblish_maya


@pyblish.api.log
class CollectRig(pyblish.api.Collector):
    """Inject all rigs from the scene into the context"""

    hosts = ["maya"]

    def process(self, context):
        from maya import cmds

        if not os.environ["TASK"] == "rigging":
            return self.log.info("No rig found")

        name = os.environ["ITEM"]

        # Get the root transform
        self.log.info("Rig found: %s" % name)
        assembly = "|{name}_GRP".format(name=name)

        assert cmds.objExists(assembly), (
            "Rig did not have an appropriate assembly: %s" % assembly)

        self.log.info("Capturing instance contents: %s" % assembly)
        instance = context.create_instance(name=name, family="rig")
        with pyblish_maya.maintained_selection():
            cmds.select(assembly)
            instance[:] = cmds.file(exportSelected=True,
                                    preview=True,
                                    constructionHistory=True,
                                    force=True)

            # Add rig-specific object sets
            for objset in ("controls_SET", "pointcache_SET"):
                if cmds.objExists(objset):
                    instance.add(objset)

        instance.set_data("preserveReferences", False)

        self.log.info("Successfully collected %s" % name)
