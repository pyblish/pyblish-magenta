import os
import shutil

import pyblish.api
import pyblish_magenta
import pyblish_magenta.schema


class IntegrateAsset(pyblish.api.Integrator):
    label = "Integrate Asset"

    def process(self, context, instance):
        extract_dir = instance.data("extractDir")

        self.log.debug("Extraction directory: %s" % extract_dir)
        assert extract_dir, (
            "Couldn't integrate %s" % instance)

        current_file = context.data("currentFile").replace("\\", "/")
        schema = pyblish_magenta.schema.load()
        data, template = schema.parse(current_file)

        task = os.environ["TASK"]

        pattern = schema.get(task + ".asset")
        assert pattern, "No schema found for %s" % task

        publish_dir = pattern.format(data)
        version = context.data("version", None)
        if version is None:
            current_versions = None
            if os.path.exists(publish_dir):
                current_versions = os.listdir(publish_dir)
                version = pyblish_magenta.find_next_version(current_versions)
            else:
                version = 1

            self.log.debug("current_versions: %s" % current_versions)
            self.log.debug("next_version: %s" % version)
            context.set_data("version", version)

        version_dir = os.path.join(publish_dir, "v%03d" % version)

        # Copy the files/directories from extract directory
        # to the integrate directory
        self.log.info("Integrating \"%s\" version %i" % (
            instance, version))

        if not os.path.exists(version_dir):
            os.makedirs(version_dir)

        for fname in os.listdir(extract_dir):
            src = os.path.join(extract_dir, fname)
            dst = os.path.join(version_dir, instance.data("family"))

            self.log.info("Copying \"%s\" to \"%s\"" % (src, dst))

            if os.path.isfile(src):
                _, ext = os.path.splitext(fname)
                dst += ext
                shutil.copy(src, dst)
            else:
                shutil.copytree(src, dst)

        self.log.info("Integrated to directory \"{0}\"".format(version_dir))
