import os
import pyblish.api
import pyblish_maya

from pyblish_magenta.utils.maya.scene import is_visible


def short_name(node):
    """Return node name without namespaces and parents"""
    return node.rsplit("|", 1)[-1].rsplit(':', 1)[-1]


@pyblish.api.log
class CollectAnimation(pyblish.api.Collector):
    """Inject meshes and cameras from the scene into the context"""

    def process(self, context):
        from maya import cmds

        if not os.environ["TASK"] == "animation":
            return self.log.info("No animation found")

        name = os.environ["ITEM"]

        # Get the point cache publish sets
        # Formatted like `<name>_pointcache_SEL`
        anim_sets = cmds.ls('*_pointcache_SEL',
                            recursive=True,
                            exactType='objectSet',
                            long=True)

        if not anim_sets:
            return

        self.log.info("Animation sets found: {0}".format(anim_sets))

        for anim_set in anim_sets:

            # Collect name
            node_name = short_name(anim_set)
            name = node_name.rsplit("_pointcache_SEL", 1)[0]

            # Collect nodes
            nodes = cmds.sets(anim_sets, query=True)
            # We only care about the dag nodes and want to ensure long names
            nodes = cmds.ls(nodes, dag=True, long=True)

            # Collect start/end frame
            attr = '{0}.startFrame'.format(anim_set)
            if cmds.objExists(attr):
                start_frame = cmds.getAttr(attr)
            else:
                start_frame = cmds.playbackOptions(query=True, minTime=True)

            attr = '{0}.endFrame'.format(anim_set)
            if cmds.objExists(attr):
                end_frame = cmds.getAttr(attr)
            else:
                end_frame = cmds.playbackOptions(query=True, maxTime=True)

            # Create the instance
            instance = context.create_instance(name=name, family="animation")
            instance[:] = nodes

            instance.set_data('startFrame', start_frame)
            instance.set_data('endFrame', end_frame)

            self.log.info("Successfully collected %s" % name)
