import os
import shutil

import pyblish.api
import pyblish_magenta.api
import pyblish_magenta.schema


class IntegrateAssets(pyblish.api.Integrator):
    """Name and position instances on disk"""

    label = "Assets"

    def process(self, context, instance):
        self.log.debug("Source file: %s" % context.data("currentFile"))

        current_file = context.data("currentFile").replace("\\", "/")
        publish_dir = self.compute_publish_directory(current_file)
        versions_dir = os.path.join(publish_dir,
                                    instance.data("family"),
                                    instance.data("name"))

        # Compute next version for this instance
        try:
            existing_versions = os.listdir(versions_dir)
            version = pyblish_magenta.api.find_next_version(existing_versions)
        except OSError:
            version = 1

        version = pyblish_magenta.api.format_version(version)

        version_dir = "{versions}/{version}".format(
            versions=versions_dir,
            version=version)

        # Copy files/directories from the temporary
        # extraction directory to the integration directory.
        extract_dir = instance.data("extractDir")

        if not extract_dir:
            return self.log.debug("Skipping %s; no files found" % instance)

        for fname in os.listdir(extract_dir):
            src = os.path.join(extract_dir, fname)
            dst = version_dir

            if os.path.isfile(src):
                try:
                    os.makedirs(dst)
                except OSError:
                    pass

                # Assembly fully-qualified name
                # E.g. thedeal_seq01_1000_animation_ben01_v002.ma
                _, ext = os.path.splitext(fname)
                filename = "{topic}_{version}_{instance}".format(
                    topic="_".join(os.environ["TOPICS"].split()),
                    instance=instance.data("name"),
                    version=version) + ext

                dst = os.path.join(dst, filename)
                self.log.info("Copying file \"%s\" to \"%s\"" % (src, dst))
                shutil.copy(src, dst)

            else:
                dst = os.path.join(dst, fname)
                self.log.info("Copying directory \"%s\" to \"%s\""
                              % (src, dst))
                shutil.copytree(src, dst)

        # Store reference for further integration
        instance.set_data("integrationDir", version_dir)

        self.log.info("Integrated to directory \"{0}\"".format(version_dir))

    def compute_publish_directory(self, path):
        """Given the current file, determine where to publish

        Arguments:
            path (str): Absolute path to the current working file

        """

        self.log.debug("Loading schema..")
        schema = pyblish_magenta.schema.load()

        self.log.debug("Parsing with current file: %s" % path)
        data, template = schema.parse(path)

        # TOPICS are a space-separated list of user-supplied topics
        # E.g. "thedeal seq01 1000 animation"
        task = os.environ["TOPICS"].split()[-1]
        assert task == data["task"], (
            "Task set in environment ({env}) is not the same as "
            "the one parsed ({data})".format(
                env=task,
                data=data["task"]))

        self.log.info("Retrieving template from schema..")
        pattern = schema.get(template.name.rsplit(
            ".work", 1)[0] + ".publish")

        self.log.info("Got \"%s\": formatting with %s" % (pattern, data))
        return pattern.format(data)
