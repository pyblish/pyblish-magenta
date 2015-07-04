import pyblish_magenta.plugin


class IntegrateAsset(pyblish_magenta.plugin.Integrator):
    label = "Integrate Asset"

    def process(self, instance):
        self.integrate(instance)
