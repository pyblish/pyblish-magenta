import pyblish.api
import pyblish_magenta.schema


@pyblish.api.log
class CollectAsset(pyblish.api.Collector):
    """Parse hierarchy of the currently opened file to determine family

    The family is determined via the absolute path as parsed
    by it's corresponding schema, see :mod:`schema.py` for more.

    """

    order = pyblish.api.Collector.order + 0.1

    def process(self, context):
        self.log.info("Collecting Asset..")

        current_file = context.data('currentFile')
        assert current_file, "Scene not saved, aborting"

        # Ensure we use a path with forward slashes
        current_file = current_file.replace('\\', '/')

        # Parse with schema
        self.log.debug("Attempting to parse current file.")
        schema = pyblish_magenta.schema.load()
        data, template = schema.parse(current_file)

        # Retrieve the family from the parsed template
        family = template.name.split('.')[0]
        context.set_data('family', family)
        self.log.debug("Family determined to be %s" % family)

        # Store the project root's path
        root = data['root']
        context.set_data('root', root)

        # Store the asset name
        asset = data['asset']
        context.set_data('asset', asset)
        self.log.debug("Storing `root={root}` and `asset={asset}` "
                       "in Context.".format(**asset))

        # Store the container's name
        if 'container' in data:
            container = data['container']
            context.set_data('container', container)
            self.log.debug("Storing `container={}` too".format(container))
