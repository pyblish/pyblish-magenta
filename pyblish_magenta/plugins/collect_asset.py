import pyblish.api
import pyblish_magenta.schema


@pyblish.api.log
class CollectAsset(pyblish.api.Collector):
    order = pyblish.api.Collector.order + 0.1

    def process(self, context):
        self.log.info("Collecting Asset..")

        work_file = context.data('workFile')
        if not work_file:
            return

        # Ensure we use a path with forward slashes
        work_file = work_file.replace('\\', '/')

        # Parse with schema
        schema = pyblish_magenta.schema.load()
        data, template = schema.parse(work_file)

        # Note that this the family id retrieved from the template.
        # This is not a one-to-one copy of the 'family' used in the plug-ins.
        # That's why we store this information as 'familyId' to avoid confusion
        family_id = template.name.split('.')[0]
        context.set_data('familyId', family_id)

        # Store the project root's path
        root = data['root']
        context.set_data('root', root)

        # Store the asset name
        asset = data['asset']
        context.set_data('asset', asset)

        # Store the container's name
        container = data['container']
        context.set_data('container', container)

