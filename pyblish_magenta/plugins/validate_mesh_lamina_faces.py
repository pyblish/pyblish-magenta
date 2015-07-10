import pyblish.api
from maya import cmds


class ValidateMeshLaminaFaces(pyblish.api.Validator):
    """Validate meshes don't have lamina faces.
    
    Lamina faces share all of their edges.

    """

    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)
    label = 'Mesh Lamina Faces'

    def process(self, instance):
        """Process all the nodes in the instance 'objectSet'"""
        meshes = cmds.ls(instance, type='mesh', long=True)

        invalid = []
        for mesh in meshes:
            if cmds.polyInfo(mesh, laminaFaces=True):
                invalid.append(mesh)

        if invalid:
            raise ValueError("Meshes found with lamina faces: {0}".format(invalid))