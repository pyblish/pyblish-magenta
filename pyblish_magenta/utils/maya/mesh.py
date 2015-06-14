from .context import TemporaryPolySelectConstraint, PreserveSelection
from maya import cmds


def polyConstraint(components, *args, **kwargs):
    """ Return the list of *components* with the constraints applied in `*args` and `**kwargs`.

    A wrapper around Maya's `polySelectConstraint` to retrieve its results as a list without altering selections.
    For the full list of possible constraint see Maya's `polySelectConstraint` documentation.

    :param components: List of components of polygon meshes
    :return: The list of components filtered by the given constraints.
    """
    with PreserveSelection():
        cmds.select(components, r=1)

        # Apply filter (and use context manager to set the polySelectConstraint settings only for this duration)
        with TemporaryPolySelectConstraint(*args,
                                           mode=3,  # All and Next so it applies to the selection just made.
                                           **kwargs):
            result = cmds.ls(sl=1)

    return result