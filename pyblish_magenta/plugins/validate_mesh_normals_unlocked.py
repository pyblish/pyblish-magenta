import pyblish.api
from maya import cmds


class ValidateMeshNormalsUnlocked(pyblish.api.Validator):
    """ Validate meshes in the instance have unlocked normals """
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)
    label = 'Mesh Normals Unlocked'

    def has_locked_normals(self, mesh):

        mesh_vertexface = cmds.polyListComponentConversion(mesh, toVertexFace=True)
        locked_normals = cmds.polyNormalPerVertex(mesh_vertexface, q=1, freezeNormal=True)
        if any(locked_normals):
            return True
        else:
            return False

    def process(self, instance):
        """ Checks all nodes for locked normals, if any found it's considered invalid. """
        meshes = cmds.ls(instance, type='mesh', long=True)

        invalid = []
        for mesh in meshes:
            if self.has_locked_normals(mesh):
                invalid.append(mesh)

        if invalid:
            raise ValueError("Meshes found with locked normals: {0}".format(invalid))

    def repair(self, instance):
        """ Unlocks all normals on the meshes in this instance. """
        meshes = cmds.ls(instance, type='mesh', long=True)
        for mesh in meshes:
            if self.has_locked_normals(mesh):
                cmds.polyNormalPerVertex(mesh, unFreezeNormal=True)
