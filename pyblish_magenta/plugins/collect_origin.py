import os
import pyblish.api
import pyblish_magenta.schema


class CollectOrigin(pyblish.api.Collector):
    """Collect metadata about referenced files in the scene"""
    label = "Source files"
    hosts = ["maya"]

    # In order to take advantage of data collected earlier
    order = pyblish.api.Collector.order + 0.1

    def process(self, context):
        from maya import cmds

        instance = context.create_instance("origin", family="metadata")

        self.log.debug("Loading schema..")
        schema = pyblish_magenta.schema.load()

        instance.set_data("metadata", {
            "project": os.environ["PROJECT"],
            "item": os.environ["ITEM"],
            "task": os.environ["TOPICS"].split()[-1],
            "author": context.data("user"),
            "date": context.data("date"),
            "filename": context.data("currentFile")
        })

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

        instance[:] = references
