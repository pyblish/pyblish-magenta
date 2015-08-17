import pyblish.api


class CollectSourceFiles(pyblish.api.Collector):
    """Collect metadata about referenced files in the scene"""
    label = "Source files"
    hosts = ["maya"]

    def process(self, context):
        from maya import cmds

        instance = context.create_instance("source", family="metadata")

        # TODO(marcus): Take into account nested references,
        # we don't want those.
        self.log.info("Collecting source files")
        source_files = [cmds.referenceQuery(reference, filename=True)
                        for reference in cmds.ls(type="reference")
                        if reference not in ("sharedReferenceNode",)]

        if source_files:
            instance[:] = source_files
            self.log.info("Found %s" % source_files)
        else:
            self.log.info("No source files found")
