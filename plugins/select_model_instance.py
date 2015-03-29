from maya import cmds
import pyblish.api
import os


def is_subdir(path, root_dir):
    """ Returns whether path is a subdirectory (or file) within root_dir """
    path = os.path.realpath(path)
    root_dir = os.path.realpath(root_dir)

    # If not on same drive
    if os.path.splitdrive(path)[0] != os.path.splitdrive(root_dir)[0]:
        return False

    # Get 'relative path' (can contain ../ which means going up)
    relative = os.path.relpath(path, root_dir)

    # Check if the path starts by going up, if so it's not a subdirectory. :)
    if relative.startswith(os.pardir) or relative == os.curdir:
        return False
    else:
        return True


def getAllParents(longName):
    parents = longName.split("|")[1:-1]
    return ['|{0}'.format('|'.join(parents[0:i+1])) for i in xrange(len(parents))]


@pyblish.api.log
class SelectModelInstance(pyblish.api.Selector):
    """ Inject all models from the scene into the context (if in modeling workspace)

        .. note:: This skips intermediate objects.
    """
    hosts = ["maya"]

    def process_context(self, context):

        """
        current_file = cmds.file(q=1, sceneName=True)
        family = utilities.family_from_path(current_file)

        if family != 'model':
            return

        asset = utilities.asset_from_path(current_file)
        """

        # must be a saved file and within a project root Directory
        project_root = cmds.workspace(q=1, rootDirectory=True)
        if not project_root:
            # this never happens?
            self.log.error("No workspace has been set.")
            return

        scene_name = cmds.file(q=1, sceneName=True)
        if not scene_name:
            # file not saved
            self.log.error("Scene has not been saved.")
            return

        # must be inside the dev modeling folder
        modeling_root = os.path.join(project_root, 'dev', 'modeling')
        if not is_subdir(scene_name, modeling_root):
            # not in modeling
            return

        # Get the asset's information
        asset_source = scene_name
        asset_root = os.path.dirname(os.path.dirname(scene_name))
        asset_name = os.path.basename(asset_root)
        asset_parent_hierarchy = os.path.dirname(asset_root[len(modeling_root):]).strip('/\\')

        # get the root transform
        root_transform = cmds.ls('|{assetName}_GRP'.format(assetName=asset_name), objectsOnly=True, type='transform')
        if not root_transform:
            return
        else:
            root_transform = root_transform[0]

        # get all children shapes (because we're modeling we only care about shapes)
        shapes = cmds.ls(root_transform, dag=True, shapes=True, long=True, noIntermediate=True)
        if not shapes:
            return

        # The nodes we want are the shape nodes including all their parents. So let's get them.
        nodes = set()
        nodes.update(shapes)
        for shape in shapes:
            nodes.update(getAllParents(shape))

        instance = context.create_instance(name=asset_name)
        instance.set_data("family", "model")
        for node in nodes:
            instance.add(node)

        # Set Pipeline data
        instance.set_data("project_root", project_root)
        instance.set_data("asset_source", asset_source)
        instance.set_data("asset_name", asset_name)
        instance.set_data("asset_parent_hierarchy", asset_parent_hierarchy)
        instance.set_data("workspace", 'modeling')

