import re

import pyblish.api
from maya import cmds


def short_name(node):
    return node.rsplit("|", 1)[-1].rsplit(":", 1)[-1]


class ValidateNoRename(pyblish.api.Validator):
    """Checks to see if there are nodes with the original names.

    If so it can be a cue for a scene/model that hasn't been cleaned yet.
    This will check for geometry related names, like nurbs & polygons.

    """

    families = ['model']
    hosts = ['maya']
    category = 'cleanup'
    optional = True
    version = (0, 1, 0)
    label = 'No Default Naming'

    __simpleNames = set(['pSphere', 'pCube', 'pCylinder', 'pCone', 'pPlane', 'pTorus',
                         'pPrism', 'pPyramid', 'pPipe', 'pHelix', 'pSolid',
                         'nurbsSphere', 'nurbsCube', 'nurbsCylinder', 'nurbsCone',
                         'nurbsPlane', 'nurbsTorus', 'nurbsCircle', 'nurbsSquare'])
    __simpleNamesRegex = [re.compile('{0}[0-9]?$'.format(x)) for x in __simpleNames]

    def process(self, instance):
        """Process all the nodes in the instance 'objectSet'"""
        transforms = cmds.ls(instance, type='transform')
        
        invalid = []
        for t in transforms:
            t_shortName = short_name(t)
            for regex in self.__simpleNamesRegex:
                if regex.match(t_shortName):
                    invalid.append(t)
                    break
            
        if invalid:
            raise ValueError("Non-renamed objects found: {0}".format(invalid))