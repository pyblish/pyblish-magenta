"""These only run once for tests in this package"""

from maya import cmds


def setup():
    # Import pymel, as opposed to maya.standalone.initialise()
    # due to pymel being imported after the fact causes the scene
    # to erase itself and start fresh, in headless mode.
    import pymel.core
    pymel.core  # Avoid PEP08 warnings

    import pyblish_maya
    pyblish_maya.register_plugins()
    pyblish_maya.register_host()


def teardown():
    # Maya throws a segmentation fault unless
    # we run the following little hack.
    # https://goo.gl/4oTQ2d
    cmds.file(new=True, force=True)
    # os._exit(0)
