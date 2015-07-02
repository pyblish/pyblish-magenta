import pyblish.api
from maya import cmds


class ValidateNamespaceEmpty(pyblish.api.Validator):
    """Validate there are no empty namespaces in the scene.

    .. note::
        This is a scene wide validation.

    .. note::
        This filters out checking the internal namespaces ['UI', 'shared'] that exist by default
        in Maya and are mostly hidden to the end user. We could also rely on the `pymel` namespace
        implementation which does that by default.
        Even though it's likely a bit slower the benefit is that it's automatically maintained and
        updated for future releases so might automatically get new internal namespaces added to it.

    """

    families = ['model']
    hosts = ['maya']
    category = 'scene'
    version = (0, 1, 0)

    __internal_namespaces = ['UI', 'shared']
    __root_namespace = ':'

    def process(self, context):
        """Process the Context"""
        all_namespaces = cmds.namespaceInfo(self.__root_namespace, listOnlyNamespaces=True, recurse=True)
        non_internal_namespaces = [ns for ns in all_namespaces if ns not in self.__internal_namespaces]

        invalid = []
        # TODO: Check whether currently a namespace with another namespace in it (both empty) is considered as empty.
        for namespace in non_internal_namespaces:
            namespace_content = cmds.namespaceInfo(namespace, listNamespace=True, recurse=True)
            if not namespace_content:
                invalid.append(namespace)

        if invalid:
            raise ValueError("Empty namespaces found: {0}".format(invalid))