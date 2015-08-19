import os

from maya import cmds


def update_reference(reference):
    """Update reference to the latest version

    Arguments:
        reference (str): Name of reference node

    """

    filename = cmds.referenceQuery(reference, filename=True)

    # NOTE(marcus): This should be based on something more
    # flexible than a fixed number of levels up a hierarchy.
    version_dir = os.path.realpath(os.path.join(filename, "..", "..", ".."))
    versions_dir = os.path.realpath(os.path.join(version_dir, ".."))
    versions = sorted(os.listdir(versions_dir))

    # Compute latest
    latest_version = versions[-1]
    old_version = os.path.basename(version_dir)

    # Compare latest with current
    new_filename = filename.replace(old_version, latest_version)

    if filename != new_filename:
        print("Updating \"%s\" from %s to %s" % (reference,
                                                 old_version,
                                                 latest_version))
        # Include environment variables.
        # NOTE(marcus): This is essential, but
        # will need to be made more forgiving.
        new_filename = new_filename.replace(
            os.environ["PROJECTROOT"], "$PROJECTROOT")

        cmds.file(new_filename, loadReference=reference)
    else:
        print("\"%s\" already up to date" % reference)


def update_selected_references():
    """Convenience method of :func:`update_reference`

    Usage:
        Select reference node, and run this function.

    """

    for reference in cmds.ls(selection=True, type="reference"):
        update_reference(reference)
