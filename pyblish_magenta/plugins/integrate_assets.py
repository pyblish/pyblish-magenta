import os
import shutil

import pyblish.api
import pyblish_magenta.api
import pyblish_magenta.schema


class IntegrateAssets(pyblish.api.Integrator):
    """Name and position instances on disk"""

    label = "Integrate Assets"

    def process(self, context):
        self.log.debug("Source file: %s" % context.data("currentFile"))

        current_file = context.data("currentFile").replace("\\", "/")
        publish_dir = self.compute_publish_directory(current_file)
        version_dir = self.compute_version_directory(publish_dir)

        # Copy files/directories from the temporary
        # extraction directory to the integration directory.
        for instance in context:
            extract_dir = instance.data("extractDir")

            if not extract_dir:
                self.log.debug("Skipping %s; no files found" % instance)
                continue

            for fname in os.listdir(extract_dir):
                src = os.path.join(extract_dir, fname)
                dst = "{root}/{family}/{name}".format(
                    root=version_dir,
                    family=instance.data("family"),
                    name=instance.data("name")).replace("/", os.sep)

                dirname = os.path.dirname(dst)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

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
        publish_template_name = template.name.rsplit(
            ".work", 1)[0] + ".publish"
        pattern = schema.get(publish_template_name)

        self.log.info("Got \"%s\": formatting with %s" % (pattern, data))
        return pattern.format(data)

    def compute_version_directory(self, path):
        """Given a directory of versions, determine the next version

        Arguments:
            path (str): Absolute path to directory with versions

        """

        try:
            existing_versions = os.listdir(path)
            version = pyblish_magenta.api.find_next_version(existing_versions)
        except OSError:
            version = 1

        return os.path.join(path, "v%03d" % version)
