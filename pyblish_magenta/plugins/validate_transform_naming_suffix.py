import pyblish.api
from maya import cmds


SUFFIX_NAMING_TABLE = {'mesh': ["_GEO"],                    # Geometry
                       # 'mesh': ["_GEO", "_GES", "_GEP"],   # (Disabled/Old) Geometry, GeometrySmooth, GeometryProxy
                       'nurbsCurve': ["_CRV"],              # Curve
                       'nurbsSurface': ["_NRB"],            # Nurbs
                       None: ['_GRP']}                      # Transform with no shapes: group

ALLOW_IF_NOT_IN_SUFFIX_TABLE = True


class ValidateTransformNamingSuffix(pyblish.api.Validator):
    """Checks whether transform naming conventions hold up for the model based on type of shape they hold.

    .. warning::
        This grabs the first child shape as a reference and doesn't use the others in the check.

    """

    families = ['model']
    hosts = ['maya']
    category = 'cleanup'
    optional = True
    version = (0, 1, 0)
    label = 'Suffix Naming Conventions'

    def is_valid_name(self, node_name, shape_type):
        """Returns whether node_name is correct for a transform containing a shape of `shape_type`.
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

    def process(self, instance):
        """Process all the nodes in the instance """
        transforms = cmds.ls(instance, type='transform', long=True)

        invalid = []
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
            raise ValueError("Incorrectly named geometry transforms: {0}".format(invalid))