import os
import shutil

import pyblish.api
import pyblish_magenta
import pyblish_magenta.schema


class IntegrateAsset(pyblish.api.Integrator):
    """Name and position instances on disk"""

    label = "Integrate Asset"

    def process(self, context, instance):
        extract_dir = instance.data("extractDir")

        self.log.debug("Source directory: %s" % extract_dir)
        assert extract_dir, (
            "Could not integrate %s: Missing \"extractDir\"" % instance)

        current_file = context.data("currentFile").replace("\\", "/")

        self.log.debug("Loading schema..")
        schema = pyblish_magenta.schema.load()
        self.log.debug("Parsing with current file: %s" % current_file)
        data, template = schema.parse(current_file)

        # TOPICS are a space-separated list of user-supplied topics
        # E.g. "thedeal seq01 1000 animation"
        task = os.environ["TOPICS"].split()[-1]
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

        self.log.info("Got \"%s\": formatting with %s" % (pattern, data))
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

        # Copy files/directories from the temporary
        # extraction directory to the integration directory.
        self.log.info("Integrating version %i" % version)

        if not os.path.exists(version_dir):
            os.makedirs(version_dir)

        for fname in os.listdir(extract_dir):
            src = os.path.join(extract_dir, fname)
            dst = os.path.join(
                version_dir,
                "%s_%s" % (instance.data("name"), instance.data("family")))
            msg = "Copying %s \"%s\" to \"%s\""

            if os.path.isfile(src):
                self.log.info(msg % ("file", src, dst))
                _, ext = os.path.splitext(fname)
                dst += ext
                shutil.copy(src, dst)
            else:
                self.log.info(msg % ("directory", src, dst))
                dst = os.path.join(dst, instance.data("family"))
                shutil.copytree(src, dst)

        self.log.info("Integrated to directory \"{0}\"".format(version_dir))
