from maya import cmds
import pyblish.api


@pyblish.api.log
class ValidateMeshHasUVs(pyblish.api.Validator):
    """Validate the current mesh has UVs.

    It validates whether the current UV set has non-zero UVs and
    at least more than the vertex count. It's not really bulletproof,
    but a simple quick validation to check if there are likely
    UVs for every face.
    """

    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    label = 'Mesh Has UVs'

    def process(self, instance):
        invalid = []

        for node in cmds.ls(instance, type='mesh'):
            uv = cmds.polyEvaluate(node, uv=True)

            if uv == 0:
                invalid.append(node)
                continue

            vertex = cmds.polyEvaluate(node, vertex=True)
            if uv < vertex:
                invalid.append(node)
                continue

        if invalid:
            raise RuntimeError("Meshes found in instance without valid UVs: {0}".format(invalid))