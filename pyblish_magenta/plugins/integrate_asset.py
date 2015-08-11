import os
import shutil

import pyblish.api
import pyblish_magenta
import pyblish_magenta.schema


class IntegrateAsset(pyblish.api.Integrator):
    label = "Integrate Asset"

    def process(self, context):
        extract_dir = context.data("extractDir")

        self.log.debug("Extraction directory: %s" % extract_dir)
        assert extract_dir, "Could not integrate"

        current_file = context.data("currentFile").replace("\\", "/")

        self.log.debug("Loading schema..")
        schema = pyblish_magenta.schema.load()

        self.log.debug("Parsing with current file: %s" % current_file)
        data, template = schema.parse(current_file)

        task = os.environ["TASK"]
        assert task == data["task"], (
            "Task set in environment ({env}) is not the same as "
            "the one parsed ({data})".format(
                env=task,
                data=data["task"]))

        # From the work template retrieve the publish template
        self.log.info("Retrieving template from schema..")
        publish_template_name = template.name.rsplit(
            ".work", 1)[0] + ".publish"
        pattern = schema.get(publish_template_name)

        self.log.info("Got %s: formatting with %s" % (pattern, data))
        publish_dir = pattern.format(data)
        version = context.data("version", None)
        if version is None:
            current_versions = None
            if os.path.exists(publish_dir):
                current_versions = os.listdir(publish_dir)
                version = pyblish_magenta.find_next_version(current_versions)
            else:
                version = 1

            self.log.debug("Current versions: %s" % current_versions)
            self.log.debug("Next version: %s" % version)
            context.set_data("version", version)

        version_dir = os.path.join(publish_dir, "v%03d" % version)

        # Copy the files/directories from extract directory
        # to the integrate directory
        self.log.info("Integrating version %i" % version)

        if not os.path.exists(publish_dir):
            os.makedirs(publish_dir)

        self.log.info("Copying \"%s\" to \"%s\"" % (extract_dir, version_dir))
        shutil.copytree(src=extract_dir, dst=version_dir)

        self.log.info("Integrated to directory \"{0}\"".format(version_dir))
