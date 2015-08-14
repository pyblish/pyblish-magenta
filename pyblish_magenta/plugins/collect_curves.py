import pyblish.api


class CollectCurves(pyblish.api.Collector):
    """Inject rigs for baking"""

    hosts = ["maya"]

    def process(self, context):
        from maya import cmds

        for pointcache in cmds.ls("controls_SET",
                                  recursive=True,
                                  exactType="objectSet",
                                  long=True):

            # Only consider objects sets part of a namespace
            if ":" not in pointcache:
                self.log.debug("Skipping \"%s\"; no namespace" % pointcache)
                continue

            nodes = cmds.sets(pointcache, query=True)
            if not nodes:
                self.log.debug("Skipping \"%s\"; empty set" % pointcache)
                continue

            # ben01_:controls_SET
            namespace, _ = pointcache.split(":", 1)
            name = namespace.strip("_") + "_anim"
            self.log.info("Found: %s" % name)

            # Create the instance
            instance = context.create_instance(name=name, family="curves")
            instance[:] = nodes

            # NOTE(marcus): This should be looked up from somewhere
            start_frame = cmds.playbackOptions(query=True, minTime=True)
            end_frame = cmds.playbackOptions(query=True, maxTime=True)

            instance.set_data("name", namespace.strip("_"))
            instance.set_data("startFrame", start_frame)
            instance.set_data("endFrame", end_frame)
            instance.set_data("publish", False)

            self.log.info("Successfully collected %s" % name)
