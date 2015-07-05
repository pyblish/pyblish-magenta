import re

import pyblish.api
from maya import cmds


def short_name(node):
    return node.rsplit("|", 1)[-1].rsplit(":", 1)[-1]


class ValidateCorrectShapeNames(pyblish.api.Validator):
    """Validates that Shape names are using Maya's default format.

    .. note::
        When you create a new polygon cube Maya will name the transform
        and shape respectively:
        - ['pCube1', 'pCubeShape1']
        If you rename it to `bar1` it will become:
        - ['bar1', 'barShape1']
        Then if you rename it to `bar` it will become:
        - ['bar', 'barShape']
        Rename it again to `bar1` it will differ as opposed to before:
        - ['bar1', 'bar1Shape']
        Note that bar1Shape != barShape1
        Thus the suffix number can be either in front of Shape or behind it.
        Then it becomes harder to define where what number should be when a
        node contains multiple shapes, for example with many controls in
        rigs existing of multiple curves.

    """

    families = ['model']
    hosts = ['maya']
    category = 'cleanup'
    optional = True
    version = (0, 1, 0)
    label = "Shape Default Naming"

    def _define_default_name(self, shape):
        transform = short_name(cmds.listRelatives(shape, parent=True, fullPath=True)[0])
        return '{0}Shape'.format(transform)

    def _is_valid(self, shape):
        """ Return whether the shape's name is similar to Maya's default. """
        transform = cmds.listRelatives(shape, parent=True, fullPath=True)[0]

        transform_name = short_name(transform)
        shape_name = short_name(shape)

        # A Shape's name can be either {transform}{numSuffix}
        # Shape or {transform}Shape{numSuffix}
        # Upon renaming nodes in Maya that is
        # the pattern Maya will act towards.
        transform_no_num = transform_name.rstrip("0123456789")
        pattern = '^{transform}[0-9]*Shape[0-9]*$'.format(
            transform=transform_no_num)

        if re.match(pattern, shape_name):
            return True
        else:
            return False

    def process(self, instance):
        """Process all the shape nodes in the instance"""
        shapes = cmds.ls(instance, shapes=True, long=True)

        invalid = []
        for shape in shapes:
            if not self._is_valid(shape):
                invalid.append(shape)

        if invalid:
            raise ValueError("Incorrectly named shapes found: {0}".format(
                invalid))

    def repair(self, instance):
        """Process all the shape nodes in the instance"""
        shapes = cmds.ls(instance, shapes=True, long=True)
        for shape in shapes:
            if not self._is_valid(shape):
                correct_shape_name = self._define_default_name(shape)
                cmds.rename(shape, correct_shape_name)
