import pyblish_magenta.utils.maya.shaders as shader_utils
from maya import cmds


class TemporaryShaders(object):
    """
        Assign the given shadingEngine temporarily to given shapes (or all descendant shapes)
    """
    def __init__(self, shapes, shading_engine="initialShadingGroup", include_descendants=True):
        self.shapes = cmds.ls(shapes, dag=include_descendants, o=1, s=1, long=1)
        self.temp_shading_engine = shading_engine
        self.original_shader_assignment = None

        if not cmds.objExists(self.temp_shading_engine):
            raise RuntimeError("shadingEngine does not exist: {0}".format(self.temp_shading_engine))

    def __enter__(self):
        self.original_shader_assignment = shader_utils.get_shader_assignment(self.shapes)
        shader_utils.perform_shader_assignment({self.temp_shading_engine: self.shapes})

    def __exit__(self, type, value, traceback):
        shader_utils.perform_shader_assignment(self.original_shader_assignment)


class TemporaryUnit():
    """
        This context sets the Maya units to the given units for the duration of the Context.
    """
    def __init__(self, unit="cm"):
        self._set_unit = unit

    def __enter__(self):
        self._original_unit = cmds.currentUnit(q=1, l=1)
        cmds.currentUnit(l=self._set_unit)

    def __exit__(self, type, value, traceback):
        cmds.currentUnit(l=self._original_unit)


class PreserveSelection(object):
    """
        A context manager then ensures selection at entering will be reapplied at exiting.
        This preserves the selection over this Context.
    """
    def __enter__(self):
        self.originalSelection = cmds.ls(sl=1)

    def __exit__(self, type, value, traceback):
        if self.originalSelection:
            cmds.select(self.originalSelection, replace=True)
        else:
            cmds.select(clear=True)


class TemporaryAutoKeyframeState(object):
    """ Temporarily changes the AutoKeyframeState """
    def __init__(self, state=False):
        self._original_state = None
        self._set_state = state

    def __enter__(self):
        self._original_state = cmds.autoKeyframe(q=1, state=True)
        cmds.autoKeyframe(state=self._set_state)

    def __exit__(self, type, value, traceback):
        if self._original_state is not None:
            cmds.autoKeyframe(state=self._original_state)


class TemporaryDisplayLayer(object):
    """ Temporarily removes the given nodes from the display layers """
    DEFAULT_LAYER = 'defaultLayer'

    def get_display_layer_relationships(self, nodes):
        from collections import defaultdict
        relationships = defaultdict(list)
        for node in nodes:
            display_layers = cmds.listConnections(node, type='displayLayer')
            if display_layers:
                display_layer = display_layers[0]
            else:
                display_layer = self.DEFAULT_LAYER

            relationships[display_layer].append(node)

        return relationships

    def __init__(self, nodes, layer=DEFAULT_LAYER):
        # ensure long names of the nodes
        self._nodes = cmds.ls(nodes, long=True, type='dagNode')
        self._to_layer = layer

    def __enter__(self):
        # Retrieve original layers per node
        self._original_layer_relationships = self.get_display_layer_relationships(self._nodes)

        # Move all nodes to the layer
        cmds.editDisplayLayerMembers(self._to_layer, self._nodes)

    def __exit__(self, type, value, traceback):
        # Move all nodes back to original layers
        for layer, nodes in self._original_layer_relationships.iteritems():
            cmds.editDisplayLayerMembers(layer, nodes)