import pyblish.api
from maya import cmds


class ValidateMeshNonZeroFaceArea(pyblish.api.Validator):
    """ Validate meshes don't have zero area faces.

        .. note:: This can be slow for high-res meshes.

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
        # // Get zero area geometry faces
        # if ($fgeom)
        # {
        # 	select -r $selectedItems;
        # 	//print ("Select geom faces between " + $minface + " " + $maxface + "\n");
        #     polySelectConstraint -m 3 -t 8 -ga on -gab $minface $maxface;
        # 	$selected = `ls -sl`;
        # 	concat( $zeroFaces, $selected );
        # 	polySelectConstraint -m 0 -t 8 -ga off;
        # }