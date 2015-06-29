import os
import shutil
import tempfile

import pyblish.api
import pyblish_magenta.schema


class Extractor(pyblish.api.Extractor):
    def temp_dir(self, instance):
        """Provide a (temporary) directory in which to store files"""
        extract_dir = instance.data('extractDir')

        if not extract_dir:
            extract_dir = tempfile.mkdtemp()
            instance.set_data('extractDir', value=extract_dir)

        return extract_dir


class Integrator(pyblish.api.Integrator):

    def compute_integrate_dir(self, instance):
        # Get instance data
        data = {'root': instance.data('root'),
                'container': instance.data('container'),
                'asset': instance.data('asset')}
        family_id = instance.data('familyId')

        if not family_id:
            raise pyblish.api.ConformError(
                "No family id found on instance. Can't resolve asset path.")

        # Get asset directory
        schema = pyblish_magenta.schema.load()
        output_template = "{0}.asset".format(family_id)
        dir_path = schema.get(output_template).format(data)

        return dir_path

    def integrate(self, instance):

        extract_dir = instance.data('extractDir')
        if not extract_dir:
            raise pyblish.api.ConformError("Cannot integrate if no `commitDir`"
                                           " temporary directory found.")

        integrate_dir = self.compute_integrate_dir(instance)

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

        # Persist path of commit within instance
        instance.set_data('integrateDir', value=integrate_dir)

        self.log.info("Integrated to directory '{0}'".format(integrate_dir))

        return integrate_dir