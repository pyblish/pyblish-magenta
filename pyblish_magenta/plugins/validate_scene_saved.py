import pyblish.api


class ValidateSceneSaved(pyblish.api.Validator):
    """Ensure the scene is saved and unmodified"""

    label = "Scene Saved (Not modified)"
    optional = True

    def process(self, context):
        assert context.data("currentFile"), "Scene not saved"
        assert not context.data('currentFileModified', False), (
            "Work file is modified. Save scene first to ensure no changes.")
