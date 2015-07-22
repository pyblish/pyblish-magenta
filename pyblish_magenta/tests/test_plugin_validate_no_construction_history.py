import os

from nose.tools import with_setup, raises, assert_raises

import pyblish.util
import pyblish.api
from maya import cmds

import pyblish_magenta
from pyblish_magenta.plugins.validate_no_construction_history import \
    ValidateNoConstructionHistory


def setup():
    # Import pymel, as opposed to maya.standalone.initialise()
    # due to pymel being imported after the fact causes the scene
    # to erase itself and start fresh, in headless mode.
    import pymel.core
    pymel.core  # Avoid PEP08 warnings

    pyblish_magenta.setup()
    os.environ["TASK"] = "modeling"
    os.environ["ITEM"] = "ben"


def teardown():
    # Maya throws a segmentation fault unless
    # we run the following little hack.
    # https://goo.gl/4oTQ2d
    cmds.file(new=True, force=True)
    os._exit(0)


def initialise():
    cmds.file(new=True, force=True)


# Invalid Meshes
@with_setup(initialise)
@raises(pyblish.api.ValidationError)
def test_validate_no_construction_history_invalid_simple():
    """Cube with default creation history is invalid."""

    # Create a cube with constructionHistory
    cmds.polyCube(name="ben_GEO", constructionHistory=True)
    cmds.group(name="ben_GRP")

    # Select and validate
    context = ItemList("name", pyblish.util.select())
    ben = context["ben"]

    validator = ValidateNoConstructionHistory()
    validator.process(ben)


@with_setup(initialise)
@raises(pyblish.api.ValidationError)
def test_validate_no_construction_history_invalid_simple():
    """Cube with (polyExtrudeFacet) history is invalid."""
    import maya.cmds as mc

    # Create a cube without constructionHistory
    cube = mc.polyCube(name='ben_GEO',
                       constructionHistory=False)
    cmds.group(name="ben_GRP")

    # Create some extrusion history
    mc.polyExtrudeFacet(cube,
                        keepFacesTogether=False,
                        localTranslateZ=0.5)

    # Select and validate
    context = ItemList("name", pyblish.util.select())
    ben = context["ben"]

    validator = ValidateNoConstructionHistory()
    validator.process(ben)


# Valid Meshes
@with_setup(initialise)
def test_validate_no_construction_history_valid_simple():
    """Cube created without constructionHistory is fine by default."""

    # Create a cube without constructionHistory
    cmds.polyCube(name="ben_GEO", constructionHistory=False)
    cmds.group(name="ben_GRP")

    # Select in context
    context = ItemList("name", pyblish.util.select())
    ben = context["ben"]

    # Process the Validator
    validator = ValidateNoConstructionHistory()
    validator.process(ben)


@with_setup(initialise)
def test_validate_no_construction_history_invalid_simple():
    """Cube with history deleted is valid, so succeeds."""
    import maya.cmds as mc

    # Create a cube without constructionHistory
    cube = mc.polyCube(name='ben_GEO',
                       constructionHistory=False)
    cmds.group(name="ben_GRP")

    # Create some extrusion history
    mc.polyExtrudeFacet(cube,
                        keepFacesTogether=False,
                        localTranslateZ=0.5)

    # Delete history
    cmds.delete(cube, constructionHistory=True)

    # Select and validate
    context = ItemList("name", pyblish.util.select())
    ben = context["ben"]

    validator = ValidateNoConstructionHistory()
    validator.process(ben)


# Invalid Mesh Repair
@with_setup(initialise)
def test_validate_no_construction_history_repair():
    """Repair using validator for construction history succeeds"""

    # Create a cube with constructionHistory
    cmds.polyCube(name="ben_GEO", constructionHistory=True)
    cmds.group(name="ben_GRP")

    # Select in context
    context = ItemList("name", pyblish.util.select())
    ben = context["ben"]

    # Process the Validator and ensure it's wrong
    validator = ValidateNoConstructionHistory()
    with assert_raises(pyblish.api.ValidationError):
        validator.process(ben)

    # Repair
    validator.repair(ben)

    # Ensure it's fixed.
    validator.process(ben)


class ItemList(list):
    """List with keys

    Raises:
        KeyError is item is not in list

    Example:
        >>> Obj = type("Object", (object,), {})
        >>> obj = Obj()
        >>> obj.name = "Test"
        >>> l = ItemList(key="name")
        >>> l.append(obj)
        >>> l[0] == obj
        True
        >>> l["Test"] == obj
        True
        >>> try:
        ...   l["NotInList"]
        ... except KeyError:
        ...   print True
        True
        >>> obj == l.get("Test")
        True
        >>> l.get("NotInList") == None
        True

    """

    def __init__(self, key, object=list()):
        super(ItemList, self).__init__(object)
        self.key = key

    def __getitem__(self, index):
        if isinstance(index, int):
            return super(ItemList, self).__getitem__(index)

        for item in self:
            if getattr(item, self.key) == index:
                return item

        raise KeyError("%s not in list" % index)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default