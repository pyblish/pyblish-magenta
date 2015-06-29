import os

import pyblish.api

from maya import cmds


@pyblish.api.log
class CollectMayaCurrentFile(pyblish.api.Collector):
    hosts = ["maya"]

    def process(self, context):
        self.log.info("Collecting Maya Work File..")

        # File Path
        # ---------
        current_file = cmds.file(q=1, sceneName=True)
        if not current_file:
            # file not saved
            self.log.error("Scene has not been saved.")
            return

        # Maya returns forward-slashes by default
        current_file = os.path.normpath(current_file)

        context.set_data('workFile', value=current_file)

