import os

from maya import cmds


def update_reference(reference):
    """Update reference to the latest version"""
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
        # Update
        cmds.file(new_filename, loadReference=reference)
    else:
        print("\"%s\" already up to date" % reference)
