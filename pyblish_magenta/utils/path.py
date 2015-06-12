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


class PathRegex(object):
    """ A utility class to define regex patterns for matching (nested) folders or a root-path.

    .. note::
        This is currently only tested on Window where it behaves as expected on local drives and network mapped drives.
    """

    # The root must be at the start of a line and can only consist of word characters and should end with :/
    FOLDERCHARS = r'[^\\/]'   # valid characters for a folder, non root
    SEPERATOR = r'[\\/]'      # valid characters for a folder seperator
    ROOT = r'^[\w]*:*[\\/]?'   # valid characters for a root path (disk drive) at start of string

    @classmethod
    def root(cls, min_count=1, max_count=None):
        """ Returns a regex group that will match the root in a path.

        By increasing the min_count/max_count beyond 1 it will include folder matching for the rest part within the
        same regex.

        .. note: If the match ends with a forward slash that will be included in the matched groups. If you don't want
                 that it's best to rstrip("/\\") -- TODO: THIS NOTE MIGHT NOT BE VALID ANYMORE, CHECK.

        Args:
            min_count (int): Defines the minimum folder count for the group
            max_count (int or None): Defines the maximum folder count for the group. A None value equals infinite.
        """
        if max_count is not None and max_count < min_count:
            raise ValueError("Max count can't define a lower count than the minimum occurences")

        if max_count is not None < 0:
            return ""

        if min_count == 1 and max_count == 1:
            return "(" + PathRegex.ROOT + ")"   # root only

        folder_min_count = None if min_count is None else min_count - 1
        folder_max_count = None if max_count is None else max_count - 1
        folder_match = "(?:" + PathRegex.folders(folder_min_count, folder_max_count)[1:]    # make non-capturing group

        return "(" + PathRegex.ROOT + folder_match + ")"

    @classmethod
    def folders(cls, min_count=1, max_count=None):
        """
            Returns a regex group that will match a folder count defined by minCount/maxCount

            If the match ends with a forward slash that will be included in the matched group, even though it is
            optional. If you don't want that it is easiest to rstrip("/\\") the result.

            @param min_count: Defines the minimum folder count for the group
            @param max_count: Defines the maximum folder count for the group, when maxCount is None it's infinite.
        """
        if max_count is not None and max_count < min_count:
            raise ValueError("Max count can't define a lower count than the minimum count")

        folder_base_regex = r"(?:(?<={0}){1}+{0}?)".format(PathRegex.SEPERATOR, PathRegex.FOLDERCHARS)

        if min_count == 0 and max_count is None:
            return "(" + folder_base_regex + "*)"                                                # zero or more folders
        if min_count == 1 and max_count is None:
            return "(" + folder_base_regex + "+)"                                                # one or more folders
        if min_count == 1 and max_count == 1:
            return "(" + folder_base_regex[3:-1] + ")"                                           # single folder
        if min_count == max_count:
            return "(" + folder_base_regex + "{" + str(min_count) + "})"                         # exact min/max folders
        if max_count is None:
            return "(" + folder_base_regex + "{" + str(min_count) + ",})"                        # at least min folders
        else:
            return "(" + folder_base_regex + "{" + str(min_count) + "," + str(max_count) + "})"  # min to max folders