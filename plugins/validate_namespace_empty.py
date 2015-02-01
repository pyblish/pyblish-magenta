import pyblish.api
from maya import cmds


class ValidateNamespaceEmpty(pyblish.api.Validator):
    """ Validate there are no empty namespaces in the scene.

        .. warning::
            At this point this does not use instances from the Context.
            Yet it's a scene wide Validation.

        .. note::
            This filters out checking the internal namespaces ['UI', 'shared'] that exist by default
            in Maya and are mostly hidden to the end user. We could also rely on the `pymel` namespace
            implementation which does that by default.
            Even though it's likely a bit slower the benefit is that it's automatically maintained and
            updated for future releases so might automatically get new internal namespaces added to it.
    """
    families = ['modeling']
    hosts = ['maya']
    category = 'scene'
    version = (0, 1, 0)

    __internal_namespaces = ['UI', 'shared']
    __root_namespace = ':'

    def process_instance(self, instance):
        """ Warning: Does not use the Context/Instance at all, but is scene-wide.
                     This also means it will repeat the exact same validation for ALL instances.
        """
        all_namespaces = cmds.namespaceInfo(self.__root_namespace, listOnlyNamespaces=True, recurse=True)
        non_internal_namespaces = [ns for ns in all_namespaces if ns not in self.__internal_namespaces]

        invalid = []
        for namespace in non_internal_namespaces:
            namespace_content = cmds.namespaceInfo(namespace, listNamespace=True, recurse=True)
            if not namespace_content:
                invalid.append(namespace)

        if invalid:
            raise ValueError("Empty namespaces found: {0}".format(invalid))