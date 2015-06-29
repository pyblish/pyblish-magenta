import pyblish_magenta.plugin


class IntegrateAsset(pyblish_magenta.plugin.Integrator):
    def process(self, instance):
        self.integrate(instance)
