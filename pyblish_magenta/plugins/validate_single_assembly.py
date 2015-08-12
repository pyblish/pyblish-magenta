import pyblish.api


class ValidateSingleAssembly(pyblish.api.Validator):
    """Ensure all nodes are in a single assembly

    Published assets must be contained within a single transform
    at the root of your outliner.

    """

    families = ['rig', 'model']
    hosts = ['maya']
    category = 'rig'
    version = (0, 1, 0)
    label = 'Single Assembly'

    def process(self, instance):
        from maya import cmds
        assemblies = cmds.ls(instance, assemblies=True)
        assert 1 == len(assemblies), (
            'Multiple assemblies found: %s' % assemblies)
