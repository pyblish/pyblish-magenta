import os

from nose.tools import with_setup

# import pyblish.api
import pyblish.util
from maya import cmds

import pyblish_magenta


def setup():
    # Import pymel, as opposed to maya.standalone.initialise()
    # due to pymel being imported after the fact causes the scene
    # to erase itself and start fresh, in headless mode.
    import pymel.core
    pymel.core  # Avoid PEP08 warnings

    pyblish_magenta.setup()
    os.environ["TASK"] = "modeling"
    os.environ["ITEM"] = "ben"


def initialise():
    cmds.file(new=True, force=True)


@with_setup(initialise)
def test_collection():
    """Collecting clean model works"""
    cmds.polyCube(name="ben_GEO")
    cmds.group(name="ben_GRP")

    context = ItemList("id", pyblish.util.select())
    context["ben"]


@with_setup(initialise)
def test_collection_contents():
    """Collecting a model without an appropriate assembly fails"""

    cmds.polyCube(name="ben_GEO")
    cmds.group(name="ben_GRP")

    cmds.createNode("mesh", name="myMesh")
    cmds.createNode("blinn", name="myShader")

    context = ItemList("id", pyblish.util.select())
    ben = context["ben"]
    print [i for i in ben]
    assert any(node.startswith("|ben_GRP") for node in ben)
    assert any(node.startswith("|ben_GRP|ben_GEO") for node in ben)
    assert not any(node.startswith("|myShader") for node in ben)
    assert not any(node.startswith("|myMesh") for node in ben)


# @with_setup(initialise)
# def test_dimensions():
#     """Publishing model with bad dimensions fails"""
#     cmds.polyCube(name="ben_GEO")
#     cmds.group(name="ben_GRP")
#     cmds.scale(1000, 1000, 1000, "ben_GEO")

#     context = pyblish.util.validate()
#     results = context.data("results")
#     # print resultsa
#     assert False


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
