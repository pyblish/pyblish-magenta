import pyblish.api


class ValidateEnvironment(pyblish.api.Validator):
    """You can only publish from a valid initial environment

    This validator looks for a pre-defined series of environment
    variables in the currently running process. If your project
    was not launched appropriately, you may not have these which
    breaks things and must therefore prevent you from publishing.

    """

    label = "Environment"

    def process(self):
        import os

        variables = ("ITEM", "TASK")
        self.log.info("Looking for %s" % str(variables))
        assert all(env in os.environ for env in variables), (
            "Environment not set-up correctly, missing %s"
            % " and ".join(variables))
        self.log.info("Found it.")
