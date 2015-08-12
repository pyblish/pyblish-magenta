import pyblish.api


class ValidateRigContents(pyblish.api.Validator):
    """Ensure rig contains pipeline-critical content

    Every rig must contain at least two object sets:
        'controls_SEL' - Set of all animatable controls
        'pointcache_SEL' - Set of all cachable meshes

    """

    label = "Rig Contents"
    families = ["rig"]
    hosts = ["maya"]

    def process(self, instance):
        missing = list()
        for objset in ("controls_SET", "pointcache_SET"):
            if objset not in instance:
                missing.append(objset)

        self.log.debug("All content: %s" % map(str, instance))
        assert not missing, ("%s is missing %s"
                             % (instance, missing))
