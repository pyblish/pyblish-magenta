import pyblish.api
from maya import cmds
import re


SUFFIX_NAMING_TABLE = {'mesh': ["_GEO", "_GES", "_GEP"],    # Geometry, GeometrySmooth, GeometryProxy
                       'nurbsCurve': ["_CRV"],              # Curve
                       'nurbsSurface': ["_NRB"],            # Nurbs
                       None: ['_GPR']}                      # Transform with no shapes: group

ALLOW_IF_NOT_IN_SUFFIX_TABLE = True


class ValidateTransformNamingSuffix(pyblish.api.Validator):
    """ Checks whether transform naming conventions hold up for the model based on type of shape they hold.

        .. warning::
            This grabs the first child shape as a reference and doesn't use the others in the check.
    """
    families = ['modeling']
    hosts = ['maya']
    category = 'cleanup'
    optional = True
    version = (0, 1, 0)

    def is_valid_name(self, node_name, shape_type):
        """ Returns whether node_name is correct for a transform containing a shape of `shape_type`.
            :rtype: bool
        """
        if shape_type not in SUFFIX_NAMING_TABLE:
            return ALLOW_IF_NOT_IN_SUFFIX_TABLE
        else:
            suffices = SUFFIX_NAMING_TABLE[shape_type]
            for suffix in suffices:
                if node_name.endswith(suffix):
                    return True
            return False

    def process_instance(self, instance):
        """Process all the nodes in the instance 'objectSet' """
        member_nodes = cmds.sets(instance.name, q=1)

        invalid = []
        transforms = cmds.ls(member_nodes, type='transform', long=True)
        for transform in transforms:
            shapes = cmds.listRelatives(transform, shapes=True, fullPath=True)

            if not shapes:  # null/group transform
                if not self.is_valid_name(transform, None):
                    invalid.append(transform)

            else:  # based on actual shape type of first child shape
                shape_type = cmds.nodeType(shapes[0])
                if not self.is_valid_name(transform, shape_type):
                    invalid.append(transform)

        if invalid:
            raise ValueError("Incorrectly named geometry transforms found: {0}".format(invalid))