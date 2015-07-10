import re


def find_next_version(versions):
    """Return next version from list of versions

    If multiple numbers are found in a single version,
    the last one found is used. E.g. (6) from "v7_22_6"

    Arguments:
        versions (list): Version numbers as string

    Example:
        >>> find_next_version(["v001", "v002", "v003])
        4
        >>> find_next_version(["1", "2", "3])
        4
        >>> find_next_version(["v1", "v0002", "verision_3])
        4
        >>> find_next_version(["v2", "5_version", "verision_8])
        9
        >>> find_next_version(["v2", "v3_5", "_1_2_3", "7, 4"])
        6

    """

    highest_version = 0
    for version in versions:
        match = re.match(r".*(\d+)", version)

        if not match:
            continue

        version = int(match.group(1))
        if version > highest_version:
            highest_version = version

    return highest_version + 1
