import os
import shutil

import pyblish.api


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
        root = repeat(5, os.path.dirname, input_path)
        output_path = os.path.join(root,
                                   "asset",
                                   "model",
                                   "characters",
                                   "ben",
                                   "conceptArt")
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


def repeat (n, f, x):
    for i in range(n):
        x = f(x)
    return x

