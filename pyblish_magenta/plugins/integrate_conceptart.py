import os
import shutil

import pyblish.api
import pyblish_magenta.schema


@pyblish.api.log
class ConformConceptArt(pyblish.api.Conformer):
    """Conform concept art to final destination

    .. note:: The final destination is overwritten
        for each publish.

    """

    families = ["conceptArt"]

    def process(self, instance):
        # in  = thedeal/dev/conceptArt/characters/ben/ben_model.png
        # out = thedeal/asset/model/characters/ben/conceptArt
        input_path = instance.data("path")

        self.log.info("Conforming %s" % input_path)
        self.log.info("Assuming environment variable: PROJECTROOT")

        if "PROJECTROOT" not in os.environ:
            raise Exception("Missing environment variable \"PROJECTROOT\"")

        schema = pyblish_magenta.schema.load()
        data, template = schema.parse(input_path)

        self.log.info("Schema successfully parsed")
        new_name = template.name.replace('dev', 'asset')
        asset_template = schema.get_template(new_name)
        output_path = asset_template.format(data)
        self.log.info("Output path successfully generated: %s" % output_path)

        self.log.info("Conforming %s to %s" %
                      (instance, "..." + output_path[-35:]))

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        try:
            shutil.copy(input_path, output_path)
        except:
            raise pyblish.api.ConformError("Could not conform %s" % instance)
        else:
            self.log.info("Successfully conformed %s!" % instance)
