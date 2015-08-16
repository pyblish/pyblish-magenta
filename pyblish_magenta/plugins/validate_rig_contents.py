import pyblish.api


class ValidateRigContents(pyblish.api.Validator):
    """Ensure rig contains pipeline-critical content

    Every rig must contain at least two object sets:
        "controls_SET" - Set of all animatable controls
        "pointcache_SET" - Set of all cachable meshes

    """

    label = "Rig Contents"
    families = ["rig"]
    hosts = ["maya"]

    def process(self, instance):
        from maya import cmds

        objsets = ("controls_SET", "pointcache_SET")

        missing = list()
        for objset in objsets:
            if objset not in instance:
                missing.append(objset)

        assert not missing, ("%s is missing %s"
                             % (instance, missing))

        not_meshes = list()
        self.log.info("Evaluating contents of object sets..")
        for node in cmds.sets("pointcache_SET", query=True):
            shapes = list()
            for shape in cmds.listRelatives(node,
                                            shapes=True,
                                            fullPath=True):
                shapes.append(shape)
                if cmds.nodeType(shape) != "mesh":
                    not_meshes.append(shape)

        not_transforms = list()
        for node in cmds.sets("controls_SET", query=True):
            if cmds.nodeType(node) != "transform":
                not_meshes.append(node)

        assert not_transforms == [], (
            "Only transforms can be part of the controls_SET: %s"
            % not_transforms)

        assert not_meshes == [], (
            "Only meshes can be part of the pointcache_SET: %s"
            % not_meshes)
