# stdlib
from collections import OrderedDict

# local lib
import pyblish_magenta.utils.maya.shaders as shader_utils
import pyblish_magenta.utils.maya.scene as scene_utils

# maya lib
from maya import cmds
import maya.mel
import pymel.core


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


class TemporaryUnit(object):
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
        self.originalSelection = cmds.ls(sl=1, long=True)

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


class TemporaryUnparent(object):
    """ Temporarily unparent the given nodes for the duration of this context.

        .. note::
            Useful for exporting a hierarchy of nodes (from root node) while excluding these bastards.

        .. warning::
            Unparenting an object (especially when not in relative mode) can cause to create extra keys on an object
            if Maya's auto keying mode is on. You could this Context together with the `TemporaryAutoKeyframeState` to
            avoid that alltogether.

        :param nodes: list of objects to unparent
        :type nodes: list, tuple, set
    """
    def __init__(self, nodes, preserve_order=True, temporary_parent=None, relative=True):

        self.__preserve_order = preserve_order
        if self.__preserve_order:
            self.__dag_order = scene_utils.get_dag_order()

        self.__unparent_nodes = nodes
        self.__temporary_parent = pymel.core.PyNode(temporary_parent) if temporary_parent else None
        self.__relative = relative

        self._original_parents = OrderedDict()
        self._original_names = {}

    def __enter__(self):
        for node in self.__unparent_nodes:
            self.unparent(node)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # First parent everything back
        for node, parent in self._original_parents.iteritems():
            node.setParent(parent, relative=self.__relative)

            # Rename back if node name has changed.
            origName = self._original_names[node]
            if node.nodeName() != origName:
                node.rename(origName)

        # Assign the original index order in the list
        # We do this in the order of the stored order
        if self.__preserve_order:
            for node, index in self.__dag_order.iteritems():
                pyNode = pymel.core.PyNode(node)
                if pyNode in self._original_parents:
                    cmds.reorder(pyNode.fullPath(), front=True)
                    cmds.reorder(pyNode.fullPath(), relative=index)

    def unparent(self, node):
        """ Unparents the node from where it is in the hierarchy and puts it under the temporary parent.
            Then it adds it into the `original parents` dict for when it exits.
        """
        if not isinstance(node, pymel.core.PyNode):
            node = pymel.core.PyNode(node)

        if not isinstance(node, pymel.core.nodetypes.DagNode):
            return

        if pymel.core.objectType(node, isAType="shape"):
            return

        parent = node.getParent()

        if self.__temporary_parent != parent:
            self._original_names[node] = node.nodeName()     # store name because it might change if not unique
            self._original_parents[node] = parent
            node.setParent(self.__temporary_parent, relative=self.__relative)


class TemporaryObjectSetSolo(object):
    """
        Temporarily removes all members in the objectSet and keeps only the given nodes in it.
    """
    def __init__(self, nodes, object_set, force_member=False):
        """
        :param nodes: The nodes to solo out in the set.
        :param object_set: The object set to operate on.
        :param force_member: If True adds the nodes to the object set whilst solo-ing even if not already a member.
        """
        self.__object_set = object_set
        self.__nodes = pymel.core.ls(nodes)
        self.__original_members = []
        self.__force_member = force_member

    def __enter__(self):
        self.__original_members = cmds.sets(self.__object_set, q=1)

        # define new members based on settings
        new_members = self.__nodes
        if not self.__force_member:
            original_members_lookup = set(pymel.core.ls(self.__original_members))
            new_members = self.__nodes if self.__force_member else \
                          [node for node in self.__nodes if node in original_members_lookup]

        # remove all members
        cmds.sets(self.__original_members, e=True, remove=self.__object_set)

        # add new members
        cmds.sets(new_members, e=True, forceElement=self.__object_set)

    def __exit__(self, exc_type, exc_val, exc_tb):

        # remove all members
        current_members = cmds.sets(self.__object_set, q=1)
        cmds.sets(current_members, e=True, remove=self.__object_set)

        # add original members
        cmds.sets(self.__original_members, e=True, forceElement=self.__object_set)


class TemporaryDisableMaya(object):
    """ Disables all Maya windows and panels to speed up things
        that require updating the time within the script.

        Windows are disabled by minimizing them.
    """
    DEFAULT_WINDOWS = ['MayaWindow', 'CommandWindow']

    def __init__(self):
        self.gMainPane = maya.mel.eval('$tmp = $gMainPane;')
        self.stored_window_states = {}

    def __set_main_state(self, state):
        cmds.paneLayout(self.gMainPane, e=1, m=state)

    def revert_to_state(self, state):
        self.__set_main_state(state)

        for window, state in self.stored_window_states.iteritems():
            if cmds.window(window, q=1, exists=1):
                cmds.window(window, e=True, i=state)

    def set_state(self, state, store_state=True):
        self.__set_main_state(state)

        # set window states
        windows = cmds.lsUI(type='window')
        for window in windows:
            if window not in self.DEFAULT_WINDOWS:
                if cmds.window(window, q=1, exists=1):
                    if store_state:
                        current_state = cmds.window(window, q=True, i=True)
                        self.stored_window_states[window] = current_state
                    cmds.window(window, e=1, i=not state)

    def __enter__(self):
        self.set_state(False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.revert_to_state(True)


class TemporarySmoothPreviewSimple(object):

    _enabled_state = {'divisionsU': 3, 'divisionsV': 3, 'pointsWire': 16, 'pointsShaded': 4, 'polygonObject': 3}
    _disabled_state = {'divisionsU': 0, 'divisionsV': 0, 'pointsWire': 4, 'pointsShaded': 1, 'polygonObject': 1}

    def __get_state(self, node):

        result = {}
        for key, default_value in self._disabled_state.iteritems():
            value = cmds.displaySmoothness(node, **{'query': True, key: True})  # returns a list or None
            result[key] = value[0] if value is not None else default_value

        return result

    def __init__(self, nodes, state):
        self._nodes = nodes
        self._state = state
        self.stored_node_states = {}

    def __enter__(self):
        # Store the original states
        self.stored_node_states.clear()
        for node in self._nodes:
            self.stored_node_states[node] = self.__get_state(node)

        # Set the states for the context
        if self._state:
            cmds.displaySmoothness(self._nodes, **self._enabled_state)
        else:
            cmds.displaySmoothness(self._nodes, **self._disabled_state)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore the original states
        for node, state in self.stored_node_states.iteritems():
            cmds.displaySmoothness(node, **state)


class TemporaryPolySelectConstraint(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._stored_state = None

    def __enter__(self):
        # Store current state
        self._stored_state = cmds.polySelectConstraint(query=True, stateString=True)
        # Set the new state
        cmds.polySelectConstraint(*self._args, **self._kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):

        # Restore the original poly select constraint
        if self._stored_state:
            maya.mel.eval(self._stored_state)


class UndoChunk(object):
    def __init__(self, name='UndoChunk'):
        self._name = name

    def __enter__(self):
        cmds.undoInfo(openChunk=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(closeChunk=True)


class NoUndo(object):
    def __init__(self, flush=True):
        self._original_state = True
        self._state_keyword = 'state' if flush else 'stateWithoutFlush'

    def __enter__(self):
        self._original_state = cmds.undoInfo(q=1, state=1)

        cmds.undoInfo(**{self._state_keyword: False})

    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(**{self._state_keyword: self._original_state})
