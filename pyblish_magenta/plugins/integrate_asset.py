import os
import shutil

import pyblish.api
import pyblish_magenta


class IntegrateAsset(pyblish.api.Integrator):
    label = "Integrate Asset"

    def process(self, instance):
        self.integrate(instance)

    def compute_integrate_dir(self, instance):
        # Get instance data
        data = {'root': instance.data('root'),
                'container': instance.data('container', None),
                'asset': instance.data('asset')}

        family = instance.data('family')
        if not family:
            raise pyblish.api.ConformError(
                "No family found on instance. Can't resolve asset path.")

        # Get asset directory
        schema = pyblish_magenta.schema.load()
        output_template = "{0}.asset".format(family)
        integrate_dir = schema.get(output_template).format(data)

        # Get version directory
        version = instance.data('version', 1)
        version_dir = 'v{0:03d}'.format(version)

        output_path = os.path.join(integrate_dir, version_dir)

        return output_path

    def integrate(self, instance):

        # Get the extracted directory
        extract_dir = instance.data('extractDir')
        if not extract_dir:
            raise pyblish.api.ConformError("Cannot integrate if no `extractDir` "
                                           "temporary directory found.")

        # Define the integrate directory
        integrate_dir = self.compute_integrate_dir(instance)
        instance.set_data('integrateDir', value=integrate_dir)

        # Copy the files/directories from extract directory to the integrate directory
        self.log.info("Integrating extracted files for '{0}'..".format(instance))
        if os.path.isdir(integrate_dir):
            self.log.info("Existing directory found, merging..")
            for fname in os.listdir(extract_dir):
                abspath = os.path.join(extract_dir, fname)
                commit_path = os.path.join(integrate_dir, fname)
                shutil.copy(abspath, commit_path)
        else:
            self.log.info("No existing directory found, creating..")
            shutil.copytree(extract_dir, integrate_dir)

        self.log.info("Integrated to directory '{0}'".format(integrate_dir))

        return integrate_dir