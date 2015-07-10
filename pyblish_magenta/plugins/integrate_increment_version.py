import pyblish.api


class IntegrateIncrementVersion(pyblish.api.Integrator):
    """ Increments the output published version before integrating. """
    order = pyblish.api.Integrator.order - 0.1
    optional = True
    #active = False

    label = "Increment Asset Version"

    def process(self, instance):
        version = instance.data("version", None)

        if not version:
            version = 1
        else:
            version += 1

        instance.set_data("version", version)