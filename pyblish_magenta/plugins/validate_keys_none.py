import pyblish.api
from maya import cmds


class ValidateKeysNone(pyblish.api.Validator):
    """ Validates that none of the nodes in the instance have any keys """
    families = ['model', 'layout']
    hosts = ['maya']
    category = 'cleanup'
    optional = True
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Process all the nodes in the instance """
        if not instance:
            # Maya's keyframe command errors out on an empty list so we return if not anything in the instance.
            return

        # quick check
        any_keys = cmds.keyframe(instance, q=1, selected=False)
        if not any_keys:
            return

        # find each individual node with keys
        invalid = []
        for node in instance:
            keys = cmds.keyframe(node, q=1, selected=False)
            if keys:
                invalid.append(node)

        if invalid:
            raise ValueError("Nodes with keys found: {0}".format(invalid))