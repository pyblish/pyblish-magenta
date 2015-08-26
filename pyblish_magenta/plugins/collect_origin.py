import os
import pyblish.api


class CollectOrigin(pyblish.api.Collector):
    """Collect metadata about current asset"""
    label = "Origin"

    # In order to take advantage of data collected earlier
    order = pyblish.api.Collector.order + 0.1

    def process(self, context):
        if "origin" not in context:
            context.create_instance("origin", family="metadata")

        instance = context["origin"]

        instance.set_data("metadata", {
            "project": os.environ["PROJECT"],
            "item": os.environ["ITEM"],
            "task": os.environ["TOPICS"].split()[-1],
            "author": context.data("user"),
            "date": context.data("date"),
            "filename": context.data("currentFile")
        })

        self.log.info("Collected %s" % instance.data("metadata"))
