import os
import pyblish_magenta.plugin


class ExtractComment(pyblish_magenta.plugin.Extractor):
    optional = True
    label = "Comment"

    def process(self, context):
        if not context.has_data("comment"):
            return self.log.info("No comment found")

        dir_path = self.temp_dir(context)
        filepath = os.path.join(dir_path, "comment.txt")

        self.log.info("Writing comment..")
        comment = context.data("comment")
        with open(filepath, "w") as f:
            f.write(comment)
        self.log.info("Comment successfully written!")
