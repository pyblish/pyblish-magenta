import os
import pyblish_magenta.api


class ExtractComment(pyblish_magenta.api.Extractor):
    families = ["comment"]
    optional = True
    label = "Comment"

    def process(self, instance):
        dir_path = self.temp_dir(instance)
        filepath = os.path.join(dir_path, "comment.txt")

        self.log.info("Writing comment..")
        comment = instance.data("value", "")
        with open(filepath, "w") as f:
            f.write(comment)
        self.log.info("Comment successfully written!")
