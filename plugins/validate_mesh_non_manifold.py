import pyblish.api
from maya import cmds


class ValidateMeshNonManifold(pyblish.api.Validator):
    """ Validate meshes don't have non-manifold edges or vertices """
    families = ['modeling']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Process all the nodes in the instance 'objectSet' """
        member_nodes = cmds.sets(instance.name, q=1)
        meshes = cmds.ls(member_nodes, type='mesh', dag=True, long=True)

        invalid = []
        for mesh in meshes:
            if cmds.polyInfo(mesh, nonManifoldVertices=True) or cmds.polyInfo(mesh, nonManifoldEdges=True):
                invalid.append(mesh)

        if invalid:
            raise ValueError("Meshes found with non-manifold edges/vertices: {0}".format(invalid))