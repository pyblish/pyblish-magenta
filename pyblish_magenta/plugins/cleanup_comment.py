import pyblish.api


class CleanupComment(pyblish.api.Plugin):
    """Clear working scene of temporal information"""
    label = "Maya Cleanup"
    order = 99
    hosts = ["maya"]
    optional = True

    def process(self, context):
        from maya import cmds
        if cmds.objExists("comment.notes"):
            cmds.setAttr("comment.notes", "", type="string")
