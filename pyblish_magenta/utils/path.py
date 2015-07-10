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

    # Check if the path starts by going up, if so it's not a subdirectory.
    if relative.startswith(os.pardir) or relative == os.curdir:
        return False
    else:
        return True


def sanitize_path(path, separator=os.sep):
    """
    Sanitize and clean up paths that may be incorrect.

    The following modifications will be carried out:

    None returns None

    Trailing slashes are removed:
    1. /foo/bar      - unchanged
    2. /foo/bar/     - /foo/bar
    3. z:/foo/       - z:\foo
    4. z:/           - z:\
    5. z:\           - z:\
    6. \\foo\bar\    - \\foo\bar
    Double slashes are removed:
    1. //foo//bar    - /foo/bar
    2. \\foo\\bar    - \\foo\bar

    :param path: the path to clean up
    :param separator: the os.sep to adjust the path for. / on nix, \ on win. defaults to: os.sep
    :returns: cleaned up path
    """
    if path is None:
        return None

    # first, get rid of any slashes at the end
    # after this step, path value will be "/foo/bar", "c:" or "\\hello"
    path = path.rstrip("/\\")

    # add slash for drive letters: c: --> c:/
    if len(path) == 2 and path.endswith(":"):
        path += "/"

    # and convert to the right separators
    # after this we have a path with the correct slashes and no end slash
    local_path = path.replace("\\", separator).replace("/", separator)

    # now weed out any duplicated slashes. iterate until done
    while True:
        new_path = local_path.replace("//", "/")
        if new_path == local_path:
            break
        else:
            local_path = new_path

    # for windows, remove duplicated backslashes, except if they are
    # at the beginning of the path
    while True:
        new_path = local_path[0] + local_path[1:].replace("\\\\", "\\")
        if new_path == local_path:
            break
        else:
            local_path = new_path

    return local_path