import pyblish.api
from maya import cmds
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


class ValidateReferencesPublished(pyblish.api.Validator):
    """Ensure all references are coming from the 'published' location. 
        
       Note: The 'published' location can hugely differ per pipeline.
             But this will give a good example on how to go about an implementation.
        """
    families = ['layout']
    hosts = ['maya']
    category = 'layout'
    optional = False
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Process all the nodes in the instance 'objectSet' """
        member_nodes = cmds.sets(instance.name, q=1)
        
        # Note: cmds.ls(referencedNodes=True) is only available in newer versions of Maya (2011+?)
        # In older versions the parameter was called `readOnly`, though that is currently obsolete (2015).
        referenced_nodes = cmds.ls(member_nodes, referencedNodes=True)
        invalid = set()
        seen = set()

        # Get the directory it should be referenced from (we'll assume `{projectRoot}/asset`)
        projectRoot = cmds.workspace(q=1, rootDirectory=True)
        assetRoot = os.path.join(projectRoot, 'asset')

        for node in referenced_nodes:
            referenced_file = cmds.referenceQuery(node, filename=True, withoutCopyNumber=True)
            if referenced_file not in seen:
                seen.add(referenced_file)
                if not is_subdir(referenced_file, assetRoot):
                    invalid.add(referenced_file)

        if invalid:
            raise ValueError("Referenced files found that are not from published assets: {0}".format(invalid))
