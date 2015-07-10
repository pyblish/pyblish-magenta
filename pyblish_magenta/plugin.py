import os
import shutil
import tempfile

import pyblish.api
import pyblish_magenta.schema


class Extractor(pyblish.api.Extractor):
    def temp_dir(self, instance):
        """Provide a (temporary) directory in which to store files"""
        extract_dir = instance.data('extractDir')

        if not extract_dir:
            extract_dir = tempfile.mkdtemp()
            instance.set_data('extractDir', value=extract_dir)

        return extract_dir