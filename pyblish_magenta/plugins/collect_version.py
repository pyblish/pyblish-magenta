import os
import re

import pyblish.api
import pyblish_magenta.schema


@pyblish.api.log
class CollectVersion(pyblish.api.Collector):
    """ Collect the `version` data into the instance. """
    order = pyblish.api.Collector.order + 0.45

    def process(self, instance):
        self.log.info("Collecting Version..")

        # Get family
        family = instance.data('family')

        # Get template
        schema = pyblish_magenta.schema.load()
        template_name = "{0}.asset".format(family)
        template = schema.get_template(template_name)

        # Get the output path (commitDir)
        output_path = template.format(instance.data())

        # Check the current versions (directories named v001, v002, v003, etc.)
        highest_version = 0
        publish_dirs = next(os.walk(output_path))[1]

        for publish_dir in publish_dirs:

            match = re.match(r"^v(\d+)$", publish_dir)
            if match:
                version = int(match.group(1))
                if version > highest_version:
                    highest_version = version

        instance.set_data("version", highest_version)
