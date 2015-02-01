import pyblish.api
from maya import cmds


class ValidateMeshNonZeroEdges(pyblish.api.Validator):
    """ Validate meshes don't have edges with a zero length.
        Also see: http://help.autodesk.com/view/MAYAUL/2015/ENU/?guid=Mesh__Cleanup """
    families = ['modeling']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)

    __tolerance = 1e-8

    def process_instance(self, instance):
        """Process all the nodes in the instance 'objectSet' """
        member_nodes = cmds.sets(instance.name, q=1)
        meshes = cmds.ls(member_nodes, type='mesh', dag=True, long=True)

        raise NotImplementedError("Needs to be implemented")

        # This is how polyCleanup does it: #
        # select -r $selectedItems;
        # //print ("Select edges between " + $minedge + " " + $maxedge + "\n");
        # polySelectConstraint -m 3 -t 0x8000 -l on -lb $minedge $maxedge;
        # $selected = `ls -sl`;
        # concat( $edges, $selected );
        # polySelectConstraint -m 0 -t 0x8000 -l off;