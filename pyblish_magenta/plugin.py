import tempfile
import pyblish.api


class Extractor(pyblish.api.Extractor):
    def temp_dir(self, context):
        """Provide a temporary directory in which to store extracted files"""
        extract_dir = context.data('extractDir')

        if not extract_dir:
            extract_dir = tempfile.mkdtemp()
            context.set_data('extractDir', value=extract_dir)

        return extract_dir
