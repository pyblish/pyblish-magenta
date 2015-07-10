import pyblish.api
from maya import cmds


class ValidateNodeNoGhosting(pyblish.api.Validator):
    """Ensure nodes do not have ghosting enabled.

    .. note::
        If one would publish towards a non-Maya format it's likely that stats like ghosting won't be exported,
        eg. exporting to Alembic.

        Instead of creating many micro-managing checks to ensure attributes have not been changed from their default
        it could be more efficient to export to a format that will never hold such data anyway.

    """

    families = ['model']
    hosts = ['maya']
    category = 'model'
    optional = False
    version = (0, 1, 0)

    _attributes = {'ghosting': 0}
    label = "No Ghosting"

    def process(self, instance):
        # Transforms and shapes seem to have ghosting
        nodes = cmds.ls(instance, long=True, type=['transform', 'shape'])
        invalid = []
        for node in nodes:
            for attr, required_value in self._attributes.iteritems():
                if cmds.attributeQuery(attr, node=node, exists=True):

                    value = cmds.getAttr('{node}.{attr}'.format(node=node, attr=attr))
                    if value != required_value:
                        invalid.append(node)

        if invalid:
            raise ValueError("Nodes with ghosting enabled found: {0}".format(invalid))
