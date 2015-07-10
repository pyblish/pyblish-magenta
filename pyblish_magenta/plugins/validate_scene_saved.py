import pyblish.api
import os


class ValidateSceneSaved(pyblish.api.Validator):
    """Ensure the scene is saved and hasn't been modified since last save.

    This uses the `workFile` and `workFileModified` data in the instance.
    """
    label = "Scene Saved (Not modified)"
    optional = True

    def process(self, instance):

        work_file = instance.data("workFile")
        if not work_file:
            raise pyblish.api.ValidationError("No `workFile` data in instance. File is likely unsaved.")

        if not os.path.exists(work_file):
            raise pyblish.api.ValidationError("The `workFile` does not exist: {0}.".format(work_file))

        work_file_modified = instance.data('workFileModified', False)
        if work_file_modified:
            raise pyblish.api.ValidationError("Work file is modified. Save scene first to ensure no changes.")