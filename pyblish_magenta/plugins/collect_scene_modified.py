import pyblish.api


@pyblish.api.log
class CollectSceneSaved(pyblish.api.Collector):
    """Store scene modified in context"""
    hosts = ["maya"]

    def process(self, context):
        from maya import cmds
        current_file_modified = cmds.file(q=1, modified=True)
        context.set_data('currentFileModified', current_file_modified)
