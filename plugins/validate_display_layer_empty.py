import pyblish.api
from maya import cmds


class ValidateDisplayLayerEmpty(pyblish.api.Validator):
    """ Validate there are no empty displayLayers in the scene.

        .. warning::
            At this point this does not use instances from the Context.
            Yet it's a scene wide Validation.

        .. note::
            This filters out checking the display layers that exist by default in Maya
            and are mostly hidden to the end user.
    """
    families = ['modeling']
    hosts = ['maya']
    category = 'scene'
    version = (0, 1, 0)

    __skip_layers = ['defaultLayer']

    def process_instance(self, instance):
        """ Warning: Does not use the Context/Instance at all, but is scene-wide.
                     This also means it will repeat the exact same validation for ALL instances.
        """
        invalid = []
        layers = cmds.ls(type='displayLayer')

        for layer in layers:
            if layer in self.__skip_layers:
                continue

            members = cmds.editDisplayLayerMembers(layer, q=1)
            if not members:
                invalid.append(layer)

        if invalid:
            raise ValueError("Empty displayLayers found: {0}".format(invalid))