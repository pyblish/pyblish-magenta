import os
import pyblish.api


class CollectShaders(pyblish.api.Collector):
    label = "Collect Shaders"
    hosts = ["maya"]

    IDENTIFIER = "shaded_SET"

    def process(self, context):
        from maya import cmds

        self.log.info("Looking for shader associations..")
        if not cmds.objExists(self.IDENTIFIER):
            return self.log.info("Nothing found")

        self.log.info("Gathering object sets..")
        sets = dict()
        for mesh in cmds.sets(self.IDENTIFIER, query=True):
            for shape in cmds.listRelatives(mesh, shapes=True):
                shape = cmds.ls(shape, long=True, absoluteName=True)[0]

                # Discover related object sets
                for objset in cmds.listSets(object=shape):
                    if objset not in sets:
                        sets[objset] = {
                            "uuid": cmds.getAttr(objset + ".uuid"),
                            "members": list()
                        }

        self.log.info("Gathering data..")
        for objset in sets:
            self.log.debug("From %s.." % objset)
            for member in cmds.ls(cmds.sets(objset, query=True),
                                  long=True,
                                  absoluteName=True):
                node, components = (member.rsplit(".", 1) + [None])[:2]
                if member in [m["name"] for m in sets[objset]["members"]]:
                    continue

                self.log.debug("Such as %s.." % member)
                sets[objset]["members"].append({
                    "name": node,
                    "uuid": cmds.getAttr(node + ".uuid"),
                    "components": components,
                    "properties": dict(
                        (attr, cmds.getAttr(node + "." + attr))
                        for attr in (
                            cmds.listAttr(node, userDefined=True) or [])
                        if attr != "uuid")
                })

        payload = [dict(name=key, **value) for key, value in sets.items()]

        item = os.environ["ITEM"]
        instance = context.create_instance(item, family="lookdev")

        self.log.info("Storing data: %s" % payload)
        instance.set_data("payload", payload)

        self.log.info("Storing sets: %s" % sets.keys())
        instance[:] = cmds.ls(sets.keys(), absoluteName=True, long=True)

        self.log.info("Found %s" % instance)
