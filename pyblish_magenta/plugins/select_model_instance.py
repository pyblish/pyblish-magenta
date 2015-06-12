from maya import cmds
import pyblish.api

import pyblish_magenta.schema


def get_all_parents(long_name):
    parents = long_name.split("|")[1:-1]
    return ['|{0}'.format('|'.join(parents[0:i+1])) for i in xrange(len(parents))]


@pyblish.api.log
class SelectModelInstance(pyblish.api.Selector):
    """ Inject all models from the scene into the context (if in modeling workspace)

        .. note:: This skips intermediate objects.
    """
    hosts = ["maya"]

    def process(self, context):
        self.log.info("Selecting model..")

        # File Path
        # ---------
        # Must be a saved file and within a project root directory
        root = cmds.workspace(q=1, rootDirectory=True).rstrip("/")
        if not root:
            # this never happens?
            self.log.error("No workspace has been set.")
            return

        scene_name = cmds.file(q=1, sceneName=True)
        if not scene_name:
            # file not saved
            self.log.error("Scene has not been saved.")
            return

        # Parse with schema
        schema = pyblish_magenta.schema.load()
        data = schema.get("model.dev").parse(scene_name)
        asset = data['asset']
        container = data['container']

        if not root == data['root']:
            raise RuntimeError("Parsed root doesn't match with current project root: {0} != {1}".format(data['root'],
                                                                                                        root))

        # Scene Geometry
        # --------------
        # Get the root transform
        root_transform = cmds.ls('|{asset}_GRP'.format(asset=asset), objectsOnly=True, type='transform')
        if not root_transform:
            return
        else:
            root_transform = root_transform[0]

        # Get all children shapes (because we're modeling we only care about shapes)
        shapes = cmds.ls(root_transform, dag=True, shapes=True, long=True, noIntermediate=True)
        if not shapes:
            return

        # The nodes we want are the shape nodes including all their parents. So let's get them.
        nodes = set()
        nodes.update(shapes)
        for shape in shapes:
            nodes.update(get_all_parents(shape))

        # Create Asset
        # ------------
        instance = context.create_instance(name=asset,
                                           family='model')
        for node in nodes:
            instance.add(node)

        # Set Pipeline data
        instance.set_data("root", root)
        instance.set_data("source_file", scene_name)
        instance.set_data("asset", asset)
        instance.set_data("container", container)

