import os
import pyblish.api
import pyblish.util

from nose.tools import with_setup

from maya import cmds
from . import lib


def setup():
    """All these tests relate to 'ben' of family 'model'"""
    os.environ["TASK"] = "modeling"
    os.environ["ITEM"] = "ben"


def initialise():
    """For every test, clear the scene"""
    cmds.file(new=True, force=True)


# @with_setup(initialise)
# def test_validate_display_layer_empty():
#     """Validate Empty Display Layers works well"""
#     cmds.polyCube(name="ben_GEO")
#     cmds.group(name="ben_GRP")
#     cmds.createDisplayLayer(name="myLayer", empty=True)
#     cmds.editDisplayLayerMembers("myLayer", "ben_GRP")

#     with lib.registered("CollectModel", "ValidateDisplayLayerEmpty"):
#         context = pyblish.util.publish()

#     for result in context.data("results"):
#         print result

#     print context["ben"]

#     assert "ValidateDisplayLayerEmpty" in lib.errored(context)
