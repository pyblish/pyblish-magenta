import os
import shutil

import pyblish.api


class IntegrateIncrementVersion(pyblish.api.Integrator):
    """ Increments the output published version before integerating. """
    order = pyblish.api.Integrator.order - 0.1
    optional = True
    state = False   # could this work?

    label = "Increment Asset Version"

    def process(self, instance):
        version = instance.data("version", None)

        if not version:
            version = 1
        else:
            version += 1

        instance.set_data("version", version)