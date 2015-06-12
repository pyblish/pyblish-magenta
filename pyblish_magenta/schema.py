import os
import lucidity


def load():
    """Load schema from project `project`

    Schemas are assumed to be located within a /database
    subdirectory of `project`.

    Arguments:
        project (str): Absolute path to project

    """

    project = os.environ["PROJECTROOT"]
    abspath = os.path.join(project, "database", "schema.yaml")
    return lucidity.Schema.from_yaml(abspath)
