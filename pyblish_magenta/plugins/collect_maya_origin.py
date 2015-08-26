import os
import pyblish.api
import pyblish_magenta.schema


class CollectMayaOrigin(pyblish.api.Collector):
    """Collect metadata about referenced files in the scene"""
    label = "Maya origin"
    hosts = ["maya"]

    def process(self, context):
        from maya import cmds

        if "origin" not in context:
            context.create_instance("origin", family="metadata")

        instance = context["origin"]

        self.log.debug("Loading schema..")
        schema = pyblish_magenta.schema.load()
        self.log.info("Collecting references..")

        references = dict()
        for reference in cmds.ls(type="reference"):
            if reference in ("sharedReferenceNode",):
                continue

            # Only consider top-level references
            reference = cmds.referenceQuery(reference,
                                            referenceNode=True,
                                            topReference=True)

            filename = cmds.referenceQuery(
                reference,
                filename=True,
                withoutCopyNumber=True)  # Exclude suffix {1}

            if filename in references:
                continue

            data, template = schema.parse(filename)
            project = os.path.basename(data["root"])

            self.log.info("Parsed with schema %s" % data)

            references[filename] = {
                "filename": filename,
                "project": project,
                "task": data["task"],
                "item": data["asset"]
            }

            self.log.info("Collecting %s" % references[filename])

        instance[:] = references.values()
