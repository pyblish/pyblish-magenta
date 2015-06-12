import pyblish.api
from maya import cmds


class ValidateDisplayLayerEmpty(pyblish.api.Validator):
    """ Validate there are no empty displayLayers in the scene.

        .. note::
            This is a scene wide validation.

        .. note::
            This filters out checking the display layers that exist by default in Maya
            and are mostly hidden to the end user.
    """
    families = ['model']
    hosts = ['maya']
    category = 'scene'
    version = (0, 1, 0)

    __skip_layers = ['defaultLayer']

    def process(self, context):
        """ Process the Context """
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