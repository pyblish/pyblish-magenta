import os
import logging
import contextlib

from nose.tools import with_setup

# import pyblish.api
import pyblish.util
from maya import cmds

from . import lib

log = logging.getLogger()


def setup():
    """All these tests relate to 'ben' of family 'model'"""
    os.environ["TASK"] = "modeling"
    os.environ["ITEM"] = "ben"


def initialise():
    """For every test, clear the scene"""
    cmds.file(new=True, force=True)


@with_setup(initialise)
def test_collection():
    """Collecting clean model works"""
    cmds.polyCube(name="ben_GEO")
    cmds.group(name="ben_GRP")

    with lib.registered("CollectModel"):
        context = pyblish.util.select()

    assert context["ben"]


@with_setup(initialise)
def test_collection_contents():
    """Collecting a model only includes nodes relevant to t"""

    cmds.polyCube(name="ben_GEO")
    cmds.group(name="ben_GRP")

    cmds.createNode("mesh", name="myMesh")
    cmds.createNode("blinn", name="myShader")

    with lib.registered("CollectModel"):
        context = pyblish.util.select()

    ben = context["ben"]
    assert any(node.startswith("|ben_GRP") for node in ben)
    assert any(node.startswith("|ben_GRP|ben_GEO") for node in ben)
    assert not any(node.startswith("|myShader") for node in ben)
    assert not any(node.startswith("|myMesh") for node in ben)


# Invalid Meshes
@with_setup(initialise)
def test_no_construction_history():
    """Meshes with history are invalid"""

    # Create scene
    cmds.polyCube(name="ben_GEO", constructionHistory=True)
    cmds.group(name="ben_GRP")

    with lib.registered("CollectModel", "ValidateNoConstructionHistory"):
        context = pyblish.util.publish()

    assert "ValidateNoConstructionHistory" in lib.errored(context)

    cmds.delete("ben_GEO", constructionHistory=True)

    with lib.registered("collect_model", "validate_no_construction_history"):
        context = pyblish.util.publish()

    assert not lib.errored(context)
