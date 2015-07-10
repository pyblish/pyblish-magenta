import pyblish.api


class ValidateEnvironment(pyblish.api.Validator):
    def process(self):
        import os
        assert all(env in os.environ for env in ("ITEM", "TASK")), (
            "Environment not set-up correctly, missing ITEM and TASK")
