import pyblish.api
from maya import cmds


class ValidateNoConstructionHistory(pyblish.api.Validator):
    """Ensure no construction history exists on the nodes in the instance"""

    families = ["model"]
    hosts = ["maya"]
    category = "geometry"
    label = "No Construction History"

    def process(self, instance):
        """Process all the nodes in the instance"""
        has_history = list(
            node for node in instance
            if "dagNode" not in cmds.nodeType(node, inherited=True)
        )

        assert not has_history, (
            "The following nodes have construction history: %s" % has_history)
