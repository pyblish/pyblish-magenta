import pyblish.api


class CollectComment(pyblish.api.Collector):
    """Find and collect optional comment"""
    hosts = ["maya"]

    def process(self, context):
        from maya import cmds
        if not cmds.objExists("comment"):
            return

        comment = cmds.getAttr("comment.notes")
        context.set_data("comment", comment)
